#!/usr/bin/env bash

sudo apt install python3-pip python3-argcomplete
sudo -H pip3 install pypodcastparser
sudo cp podcast_dl.py /usr/local/bin/podcast-dl
cd /usr/local/bin
sudo chmod +x podcast-dl