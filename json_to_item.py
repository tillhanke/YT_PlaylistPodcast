#!/usr/bin/env python
# coding: utf-8
import json
import sys
import xml.etree.ElementTree as ET
import datetime
import copy
import re

def parse_chapters(description):
    """
    Parses the chapter information from the episode description.

    Parameters:
    description (str): The description of the podcast episode.

    Returns:
    list of dict: A list of chapters, each represented as a dictionary with 'timestamp' and 'title'.
    """
    chapters = []
    # Regex pattern to match chapters format in the description
    # Assumes format like "00:00 - Chapter Title"
    pattern = re.compile(r'(\d{2}:\d{2}) - (.+)')
    matches = pattern.findall(description)

    for match in matches:
        timestamp, title = match
        chapters.append({'timestamp': timestamp, 'title': title.strip()})
    return chapters

# json filepath as argument
if len(sys.argv) < 2:
    print("Usage: json_to_item.py [--dry-run] <json_file>")
    exit()
if "--dry-run" in sys.argv:
    print("Dry run, not writing to file")
    dry_run = True
    sys.argv.remove("--dry-run")
else:
    dry_run = False
    
ytjson = json.load(open(sys.argv[1], "r"))
tree = ET.parse('feed.xml')
root_xml = tree.getroot()

update = False
for it in root_xml[0].findall('item'):
    if ytjson["title"] ==  it.find("title").text:
        print("Item already exists, updating")
        item = it
        update = True
        break
if update == False:
    print("Item does not exist, creating new")
    root_xml[0].append(copy.deepcopy(root_xml[0][-1]))
    item = root_xml[0][-1]

# include values from json to item
item.find("title").text = ytjson["title"]
item.find("{http://www.itunes.com/dtds/podcast-1.0.dtd}title").text = ytjson["title"]
item.find("description").text = ytjson["description"]
chapters = parse_chapters(ytjson["description"])
if len(chapters) > 0:
    print("found chapters are: " + str(chapters))
    chapters_xml = ET.Element("{https://podcastindex.org/namespace/1.0}chapters")
    for chapter in chapters:
        chapter_xml = ET.SubElement(chapters_xml, "chapter")
        chapter_xml.attrib["start"] = chapter["timestamp"]
        chapter_xml.text = chapter["title"]
    if item.find("{https://podcastindex.org/namespace/1.0}chapters") is not None:
        item.remove(item.find("{https://podcastindex.org/namespace/1.0}chapters"))
    item.append(chapters_xml)

date = datetime.date(int(ytjson["upload_date"][0:4]), int(ytjson["upload_date"][4:6]), int(ytjson["upload_date"][6:8]))
rfc2822_date = date.strftime("%a, %d %b %Y %H:%M:%S +0100")
item.find("pubDate").text = rfc2822_date
item.find("link").text = "https://youtu.be/" + ytjson["display_id"]  # youtube link
mp3_url = "https://gkraktuell.bartho.org/archive/" + ytjson["title"].split(" ")[-1] + ".mp3"

item.find("guid").text = mp3_url
item.find("{http://www.itunes.com/dtds/podcast-1.0.dtd}image").attrib["href"] = ytjson["thumbnail"]
item.find("{http://www.itunes.com/dtds/podcast-1.0.dtd}episode").text = ytjson["title"].split(" ")[-1]
item.find("enclosure").attrib["url"] = mp3_url
item.find("enclosure").attrib["length"] = str(ytjson["duration"])
item.find("{http://www.itunes.com/dtds/podcast-1.0.dtd}duration").text = str(ytjson["duration"])

# write to file
# do not write if --dry-run is set
if dry_run == False:
    root_xml[0].find("lastBuildDate").text = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0100")  # last build
    tree.write('feed.xml')
