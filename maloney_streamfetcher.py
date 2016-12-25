#!/usr/bin/python
#-------------------------------------------------------------------------------
# Import modules
#
import pycurl
from xml.dom import minidom
import os, io, re
import shutil
import argparse
#import unicodedata

#-------------------------------------------------------------------------------
# Class Maloney Download
#
class maloney_download:
  '''
  Downloads Maloney Episodes
  '''
  verbose = False

  def __init__(self, verbose=False):
    # Change to script location
    path,file=os.path.split(os.path.realpath(__file__))
    os.chdir(path)
    self.path = path
    self.verbose = verbose

  def fetch_latest(self, outdir = None, uid = None):
    srf_maloney_url   = "http://www.srf.ch/sendungen/maloney/"
    self.process_maloney_episodes(srf_maloney_url, outdir=outdir, uid=uid)

  def fetch_all(self, outdir = None, uid = None):
    srf_maloney_url    = "http://www.srf.ch/sendungen/maloney/layout/set/ajax/Sendungen/maloney/sendungen/(offset)/"

    for i in range(0,510,10): # each page shows 10 items per page, iterate through pages
      url = srf_maloney_url + str(i)
      if (self.process_maloney_episodes(url, i, outdir=outdir, uid=uid) > 0) and uid: # if uid is set and download worked -> exit
        return

  def process_maloney_episodes(self, url, offset = 0, outdir=None, uid=None):
    # Constants
    path_to_ffmpeg   = "ffmpeg"
    path_to_rtmpdump = "rtmpdump"
    path_to_mid3v2   = "python " + self.path+"/mid3v2.py"
    path_to_mid3v2   = "mid3v2"
    temp_directory   = "./temp"
    xml_url          = "http://www.srf.ch/webservice/ais/report/audio/withLiveStreams/"

    # Get user constants
    if outdir == None:
      out_dir = "."
    elif os.path.isdir(outdir):
      out_dir = outdir
    else:
      self.log("Given output directory doesn't exist")
      return None

    # Get page content and id's
    if uid == None:
      id = [0,1,2,3,4,5,6,7,8,9]
      self.log("No ID given, will download all available episodes from the mainpage")
      # Get page info
      page = self.curl_page(url)
      uids = self.parse_html(page)
    else:
      uids = [uid]

    # Read XML Data
    xml_data = self.get_xmldata(xml_url, uids)

    # Download Files
    self.log("Get Episodes")
    # Create tmp directory
    if not os.path.exists(temp_directory):
      os.makedirs(temp_directory)
    cnt = 0
    idx = []
    for episode in xml_data:
      if os.path.isfile(out_dir + "/" + episode["mp3_name"]):
        self.log("  Episode \"{} - {}\" already exists in the output folder {}".format(episode["year"], episode["title"], out_dir + "/" + episode["mp3_name"]))
        self.log("    Skipping Episode ...")
      else:
        idx.append(cnt)
        # Download with RTMP
        self.log("  RTMP download...")
        command = path_to_rtmpdump + " -r " + episode["rtmpurl"] + "  -o \"" + temp_directory + "/stream_dump.flv\""
        self.system_command(command)

        # Convert to MP3
        self.log("  FFMPEG conversion flv to MP3...")
        command = path_to_ffmpeg + " -y -loglevel panic -stats -i " + temp_directory + "/stream_dump.flv -vn -c:a copy \"" + out_dir + "/" + episode["mp3_name"] + "\""
        self.system_command(command)

        # Add ID3 Tag
        self.log("  Adding ID3 Tags...")
        command = ("{} -t \"{} - {}\" \"{}\"").format(path_to_mid3v2, episode["date"], episode["title"], out_dir + "/" + episode["mp3_name"])
        self.system_command(command)
        command = ("{} -A \"{}\" \"{}\"").format(path_to_mid3v2, "Maloney Philip", out_dir + "/" + episode["mp3_name"])
        self.system_command(command)
        command = ("{} -a \"{}\" \"{}\"").format(path_to_mid3v2, "Graf Roger", out_dir + "/" + episode["mp3_name"])
        self.system_command(command)
        command = ("{} -g \"{}\" \"{}\"").format(path_to_mid3v2, "Book", out_dir + "/" + episode["mp3_name"])
        self.system_command(command)
        command = ("{} -y \"{}\" \"{}\"").format(path_to_mid3v2, episode["year"], out_dir + "/" + episode["mp3_name"])
        self.system_command(command)
        command = ("{} -c \"{}\" \"{}\"").format(path_to_mid3v2, episode["lead"], out_dir + "/" + episode["mp3_name"])
        self.system_command(command)
      cnt = cnt + 1

    # Deleting tmp directory
    shutil.rmtree(temp_directory)

    print("------------------------------------------------------")
    print(" Finished downloading {} Episodes from page with offset {}".format(len(idx), offset))
    for id in idx:
      print("  * {}".format(out_dir + "/" + xml_data[id]["mp3_name"]))
    print("------------------------------------------------------")
    return cnt

  def curl_page(self, url):
    buffer = io.BytesIO()
    c = pycurl.Curl()
    c.setopt(c.WRITEFUNCTION, buffer.write)
    c.setopt(c.URL, url)
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()
    return buffer.getvalue().decode("utf-8")

  def parse_html(self, page):
    #lines = unicodedata.normalize('NFKD', page).encode('ascii','ignore')
    #lines = str(lines).split("\n")
    lines = str(page).split("\n")

    uids = []

    for line in lines:
      if re.search("/popupaudioplayer", line):
      #if '/popupaudioplayer' in line:
        pos = line.find("?id=") + 4
        uids.append(line[pos:-1])

    if (len(uids) > 0):
      self.log("Found ID's")
      for i in range(len(uids)):
        self.log("  * ID {} = {} ".format(i, uids[i]))
    return uids

  def get_xmldata(self, xmlurl, uids):
    xml_data = []
    for uid in uids:
      url = xmlurl + uid  + ".xml"
      page = self.curl_page(url)
      (mp3_name, title, lead, rtmpurl, year, date) = self.parse_xml(page)
      xml_data.append({"mp3_name": mp3_name, "title": title, "lead": lead, "rtmpurl":rtmpurl, "year":year, "date":date})
    return xml_data

  def parse_xml(self, xml):
    xml = unicodedata.normalize('NFKD', xml).encode('ascii','ignore') # we're not interested in any non-unicode data
    xmldoc = minidom.parseString(xml)
    title = xmldoc.getElementsByTagName('title')[0].firstChild.data
    lead = xmldoc.getElementsByTagName('lead')[0].firstChild.data
    publishedDate = xmldoc.getElementsByTagName('publishedDate')[0].firstChild.data
    rtmpurl = xmldoc.getElementsByTagName('rtmpUrl')[0].firstChild.data
    year = publishedDate[:4]
    date = publishedDate[:10]
    mp3_name = "{} - Maloney Philip - {}.mp3".format(date, title)

    self.log("    MP3 Filename: {}".format(mp3_name))
    self.log("      * Title       :{} Date:{}".format(title, publishedDate, year))
    self.log("      * RTMP Url    :{}".format(rtmpurl))
    self.log("      * Lead        :{}".format(lead))
    return(mp3_name, title, lead, rtmpurl, year, date)

  def system_command(self, command):
    self.log(command)
    os.system(command)

  def log(self, message):
    if self.verbose:
      print(message)

#-------------------------------------------------------------------------------
# Execute
#
if __name__ == "__main__":

  parser = argparse.ArgumentParser(description = 'Options for maloney_streamfetcher script')
  parser.add_argument('-a', '--all', action='store_false', dest='latest', help='Download all 500 last Maloney episodes. Does not work for the newest one or two, use -l instead.')
  parser.add_argument('-l', '--latest', action='store_true', dest="latest", help='Download the last 10 Maloney episodes, works also for the newest ones ;-).')
  parser.add_argument('-o', '--outdir', dest='outdir', help='Specify directory to store episodes to.')
  parser.add_argument('-u', '--uid', dest='uid', help='Download a single episode by providing SRF stream UID.')
  parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', help='Enable verbose.')
  args = parser.parse_args()

  latest = args.latest

  maloney_downloader = maloney_download(verbose=args.verbose)

  if latest:
    maloney_downloader.fetch_latest(outdir = args.outdir, uid=args.uid)
  else: # default setting
    maloney_downloader.fetch_all(outdir = args.outdir, uid=args.uid)