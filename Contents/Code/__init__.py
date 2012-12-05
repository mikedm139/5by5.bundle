TITLE = "5by5"
ICON = "icon-default.png"
ART = "art-default.jpg"

NAMESPACES = {'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd', 'atom10': 'http://www.w3.org/2005/Atom'}
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
    TrackObject.thumb = R(ICON)

    HTTP.CacheTime = 1800

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
            title = title
        ))

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
        duration = TimeToMs(duration_string)

        oc.add(TrackObject(
            url = url,
            title = title,
            artist = show_title,
            thumb = thumb,
            duration = duration
        ))

    return oc

####################################################################################################
def TimeToMs(timecode):

    seconds  = 0
    duration = timecode.split(':')
    duration.reverse()

    for i in range(0, len(duration)):
        seconds += int(duration[i]) * (60**i)

    return seconds * 1000
