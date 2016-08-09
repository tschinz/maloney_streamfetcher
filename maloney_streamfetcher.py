#!/usr/bin/python
#-------------------------------------------------------------------------------
# Import modules
#
import pycurl
from xml.dom import minidom
import os, io, re
import shutil

#-------------------------------------------------------------------------------
# Constants to modify
#  * output_directory default = ./
#  * uid default              = all available episodes will be downloaded
# e.g.
#output_directory = "/path/to/output/directory"
#uid              = "04f041f7-3f1f-4281-aace-4cc69c4b0a69"
output_directory = None
uid              = None

#-------------------------------------------------------------------------------
# Class Maloney Download
#
class maloney_download:
  '''
  Downloads Maloney Episodes
  '''
  def __init__(self, outdir = None, uid = None):
    # Change to script location
    path,file=os.path.split(os.path.realpath(__file__))
    os.chdir(path)

    # Constants
    path_to_ffmpeg   = "ffmpeg"
    path_to_rtmpdump = "rtmpdump"
    path_to_mid3v2   = "mid3v2"

    temp_directory   = "./temp"
    srf_maloney_url  = "www.srf.ch/sendungen/maloney"
    xml_url          = "http://www.srf.ch/webservice/ais/report/audio/withLiveStreams/"

    # Get user constants
    if outdir == None:
      out_dir = "."
    elif os.path.isdir(outdir):
      out_dir = outdir
    else:
      print("Given output directory doesn't exist")
      return -1

    # Get page content and id's
    if uid == None:
      id = [0,1,2,3,4,5,6,7,8,9]
      print("No ID given, will download all available episodes from the mainpage")
      # Get page info
      page = self.curl_page(srf_maloney_url)
      uids = self.parse_html(page)
    else:
      uids = [uid]

    # Read XML Data
    xml_data = self.get_xmldata(xml_url, uids)

    # Download Files
    print("Get Episodes")
    # Create tmp directory
    if not os.path.exists(temp_directory):
      os.makedirs(temp_directory)
    cnt = 0
    idx = []
    for episode in xml_data:
      if os.path.isfile(out_dir + "/" + episode["mp3_name"]):
        print("  Episode \"{} - {}\" already exists in the output folder {}".format(episode["year"], episode["title"], out_dir + "/" + episode["mp3_name"]))
        print("    Skipping Episode ...")
      else:
        idx.append(cnt)
        # Download with RTMP
        print("  RTMP download...")
        command = path_to_rtmpdump + " -r " + episode["rtmpurl"] + "  -o \"" + temp_directory + "/stream_dump.flv\""
        self.system_command(command)

        # Convert to MP3
        print("  FFMPEG conversion flv to MP3...")
        command = path_to_ffmpeg + " -y -loglevel panic -stats -i " + temp_directory + "/stream_dump.flv -vn -c:a copy \"" + out_dir + "/" + episode["mp3_name"] + "\""
        self.system_command(command)

        # Add ID3 Tag
        print("  Adding ID3 Tags...")
        command = ("{} -t \"{}\" \"{}\"").format(path_to_mid3v2, episode["title"], out_dir + "/" + episode["mp3_name"])
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
    print(" Finished downloading {} Episodes".format(len(idx)))
    for id in idx:
      print("  * {}".format(out_dir + "/" + xml_data[id]["mp3_name"]))
    print("------------------------------------------------------")
    return 1
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
    lines = str(page).split("\n")
    uids = []
    for line in lines:
      if re.search("/popupaudioplayer", line):
        pos = line.find("?id=") + 4
        uids.append(line[pos:-1])
    print("Found ID's")
    for i in range(len(uids)):
      print("  * ID {} = {} ".format(i, uids[i]))
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
    xmldoc = minidom.parseString(xml)
    title = xmldoc.getElementsByTagName('title')[0].firstChild.data
    lead = xmldoc.getElementsByTagName('lead')[0].firstChild.data
    publishedDate = xmldoc.getElementsByTagName('publishedDate')[0].firstChild.data
    rtmpurl = xmldoc.getElementsByTagName('rtmpUrl')[0].firstChild.data
    year = publishedDate[:4]
    date = publishedDate[:10]
    mp3_name = "{} - Maloney Philip - {}.mp3".format(date, title)
    #mp3_name = "Maloney Philip - {}.mp3".format(title)
    print("MP3 Filename: {}".format(mp3_name))
    print("  * Title       :{} Date:{}".format(title, publishedDate, year))
    #print("  * RTMP Url    :{}".format(rtmpurl))
    print("  * Lead        :{}".format(lead))
    return(mp3_name, title, lead, rtmpurl, year, date)

  def system_command(self, command):
    print(command)
    os.system(command)

#-------------------------------------------------------------------------------
# Execute
#
if not(output_directory == None) and not(uid == None):
  maloney_downloader = maloney_download(outdir = output_directory, uid = uid)
elif not(output_directory == None):
  maloney_downloader = maloney_download(outdir = output_directory)
elif not(uid == None):
  maloney_downloader = maloney_download(uid = uid)
else:
  maloney_downloader = maloney_download()