import re

BY5_MUSIC_PREFIX      = "/music/5by5"

TITLE = "5by5"
ICON = "icon-default.png"
ART = "art-default.jpg"

CACHE_INTERVAL = 1800

NAMESPACES = { 'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd', 'atom10': 'http://www.w3.org/2005/Atom' }

BROADCAST_URL = 'http://5by5.tv/radio/broadcasts/list.json'
FEED_URL = 'http://feeds.5by5.tv/%s'

####################################################################################################
def Start():
    Plugin.AddViewGroup("InfoList", viewMode = "InfoList", mediaType = "items")

    ObjectContainer.title1 = TITLE
    ObjectContainer.view_group = 'InfoList'
    ObjectContainer.art = R(ART)

    DirectoryObject.thumb = R(ICON)
    DirectoryObject.art = R(ART)
    VideoClipObject.thumb = R(ICON)
    VideoClipObject.art = R(ART)
    TrackObject.thumb = R(ICON)
    TrackObject.art = R(ART)

    HTTP.SetCacheTime(CACHE_INTERVAL)

####################################################################################################
@handler('/music/5by5', TITLE, art = ART, thumb = ICON)
def MainMenu():
    oc = ObjectContainer()

    broadcasts = JSON.ObjectFromURL(BROADCAST_URL)
    for broadcast in broadcasts['broadcasts']:

        channel = broadcast['broadcast']['slug']
        title = broadcast['broadcast']['title']
        oc.add(DirectoryObject(key = 
            Callback(ChannelMenu, channel = channel), 
            title = title))

    return oc

####################################################################################################
@route('/music/5by5/{channel}', allow_sync = True)
def ChannelMenu(channel):

    feed = XML.ElementFromURL(FEED_URL % channel)

    show_title = feed.xpath("//channel/title/text()", namespaces = NAMESPACES)[0]
    thumb = feed.xpath("//channel/itunes:image", namespaces = NAMESPACES)[0].get('href')

    oc = ObjectContainer(title2 = show_title)

    for item in feed.xpath("//item", namespaces = NAMESPACES):
        title = item.xpath(".//title/text()", namespaces = NAMESPACES)[0]
        url = item.xpath(".//guid/text()", namespaces = NAMESPACES)[0]
        
        # [Optional]
        summary = None
        try: summary = item.xpath(".//itunes:summary/text()", namespaces = NAMESPACES)[0]
        except: pass

        # The duration is in the format HH:MM:SS and therefore we must convert this into a suitable
        # number of milliseconds.
        duration_string = item.xpath(".//itunes:duration/text()", namespaces = NAMESPACES)[0]
        duration_dict = re.match("((?P<hours>[0-9]+):)?(?P<mins>[0-9]+):(?P<secs>[0-9]+)", duration_string).groupdict()

        hours = 0
        try: hours = int(duration_dict['hours'])
        except: pass
        mins = 0
        try: mins = int(duration_dict['mins'])
        except: pass
        secs = 0
        try: secs = int(duration_dict['secs'])
        except: pass
        duration = (hours * 3600 + mins * 60 + secs) * 1000
        
        oc.add(TrackObject(
            url = url,
            title = title,
            artist = show_title,
            thumb = thumb,
            duration = duration))

    return oc