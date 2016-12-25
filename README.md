[Maloney Streamfetcher](https://github.com/tschinz/maloney_streamfetcher)
================================

This Python script let your download the latest Philip Maloney Episodes from the [SRF Website](http://www.srf.ch/sendungen/maloney).

Requirements
---
* ``Python 3.0`` but should be compatible with ``Python 2.x``
  * ``pycurl``
  * ``xml.dom``
* ``rtmpdump`` - For downloading the rtmp stream
* ``ffmpeg`` - For mp3 conversion
* ``mid3v2.py`` - For create the id3 tags

On a Debian based Linux:
```bash
sudo apt-get install python3 python3-pycurl rtmpdump ffmpeg mid3v2
```

Features
---
* Lets you download all current episodes as MP3
* Lets you download the last 500 episodes as MP3
* Lets you download an episode with a known UID as MP3
* Creates ID3 tags for the episode
* Checks for duplicated episodes
* Checks for folders

Usage
---

```bash
python maloney_streamfetcher.py -h

Usage: maloney_streamfetcher.py [options]

Options:
  -h, --help            show this help message and exit
  -a, --all             Download all 500 last Maloney episodes. Does not work
                        for the newest one or two, use -l instead.
  -l, --latest          Download the last 10 Maloney episodes, works also for
                        the newest ones ;-).
  -o OUTDIR, --outdir=OUTDIR
                        Specify directory to store episodes to.
  -u UID, --uid=UID     Download a single episode by providing SRF stream UID.
  -v, --verbose         Enable verbose.
```

* Execute script
```bash
python maloney_streamfetcher.py -l -o /location/to/musicfiles
```

* Use Cronjob for automatically execute the script every Monday at 24:00.
```bash
crontab -e
```
```bash
0 * * * 1 python /location/to/maloney_streamfetcher.py -l -o /location/to/musicfiles
```

![Maloney Philip](http://www.srfcdn.ch/radio/modules/dynimages/624/drs-3/maloney/2012/142280.maloney1.jpg)


Versions Log
---
- `v1.1`
  * ADD: Using Optparse
  * ADD: replace mid3v2 with mid3v2.py
  * CHG: Merged `maloney_streamfetcher.py` and `maloney_streamfetcher_all.py`
- `v1.0`
  * Initial Release

Thanks
---
  * This work was inspired by [Stream Fetcher](https://www.ruinelli.ch/philip-maloney-stream-fetcher) of Ruinelli, a big thanks to him.
  * Thanks for `v1.1` extension to @dirtbit

Licensing
---
This document is under the [CC BY-NC-ND 3-0 License, Attribution-NonCommercial-NoDerivs 3.0 Unported](http://creativecommons.org/licenses/by-nc-nd/3.0/). Use this script at your own risc!

The Philip Maloney streams are copyright by [Roger Graf](www.rogergraf.ch). The streams are provided by [SRF](www.srf.ch/sendungen/maloney). It is against the law to distribute the generated mp3 files!