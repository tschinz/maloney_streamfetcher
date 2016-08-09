[Maloney Downloader](https://github.com/tschinz/maloney_downloader)
================================

This Python script let your download the latest Philip Maloney Episodes from the [SRF Website](http://www.srf.ch/sendungen/maloney).

Requirements
---
* ``Python 3.0`` but should be compatible with ``Python 2.x``
  * ``pycurl``
  * ``xml.dom``
* ``rtmpdump`` - For downloading the rtmp stream
* ``ffmpeg`` - For mp3 conversion
* ``mid3v2`` - For create the id3 tags

On a Debian based Linux:
```bash
sudo apt-get install python3 python3-pycurl rtmpdump ffmpeg mid3v2
```

Features
---
* Lets you download all current episodes as MP3
* Lets you download an episode with a known UID as MP3
* Creates ID3 tags for the episode
* Checks for duplicated episodes
* Checks for folders

Usage
---
* Modify constants in the script ``maloney_streamfetcher.py``
```python
#-------------------------------------------------------------------------------
# Constants to modify
#  * output_directory default = ./
#  * uid default              = all available episodes will be downloaded
# e.g.
#output_directory = "/path/to/output/directory"
#uid              = "04f041f7-3f1f-4281-aace-4cc69c4b0a69"
output_directory = None
uid              = None
```
  * if ``output_directory`` is deleted then the script location will be used ``./``
  * if ``uid`` is deleted then all available episodes will be downloaded 


* Execute script
```bash
python maloney_streamfetcher.py
```

* Use Cronjob for automatically execute the script every Monday at 24:00
```bash
0 * * * 1 python /location/to/maloney_streamfetcher.py
```

![Maloney Philip](http://www.srfcdn.ch/radio/modules/dynimages/624/drs-3/maloney/2012/142280.maloney1.jpg)


Versions Log
---
- `v1.0` - Initial Release

Thanks
---
This work was inspired by [Stream Fetcher](https://www.ruinelli.ch/philip-maloney-stream-fetcher) of Ruinelli, a big thanks to him.

Licensing
---
This document is under the [CC BY-NC-ND 3-0 License, Attribution-NonCommercial-NoDerivs 3.0 Unported](http://creativecommons.org/licenses/by-nc-nd/3.0/). Use this script at your own risc!

The Philip Maloney streams are copyright by [Roger Graf](www.rogergraf.ch). The streams are provided by [SRF](www.srf.ch/sendungen/maloney). It is against the law to distribute the generated mp3 files!