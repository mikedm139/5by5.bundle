TITLE = "5by5"
BROADCAST_URL = 'http://5by5.tv/radio/broadcasts/list.json'
FEED_URL = 'http://feeds.5by5.tv/%s'
NAMESPACES = {'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd'}

####################################################################################################
def Start():

    ObjectContainer.title1 = TITLE
    HTTP.CacheTime = CACHE_1HOUR

####################################################################################################
@handler('/music/5by5', TITLE)
def MainMenu():

    oc = ObjectContainer()
    broadcasts = JSON.ObjectFromURL(BROADCAST_URL)

    for broadcast in broadcasts['broadcasts']:
        channel = broadcast['broadcast']['slug']
        title = broadcast['broadcast']['title']

        oc.add(DirectoryObject(
            key = Callback(ChannelMenu, channel=channel),
            title = title
        ))

    return oc

####################################################################################################
@route('/music/5by5/{channel}', allow_sync=True)
def ChannelMenu(channel):

    feed = XML.ElementFromURL(FEED_URL % channel)
    show_title = feed.xpath("//channel/title/text()")[0]
    thumb = feed.xpath("//channel/itunes:image/@href", namespaces=NAMESPACES)[0]
    oc = ObjectContainer(title2=show_title)

    for item in feed.xpath("//item"):
        title = item.xpath(".//title/text()")[0]
        url = item.xpath(".//guid/text()")[0]

        # [Optional]
        try: summary = item.xpath(".//itunes:summary/text()", namespaces=NAMESPACES)[0]
        except: summary = None

        # The duration is in the format HH:MM:SS and therefore we must convert this into a suitable
        # number of milliseconds.
        duration_string = item.xpath(".//itunes:duration/text()", namespaces=NAMESPACES)[0]
        duration = Datetime.MillisecondsFromString(duration_string)

        oc.add(TrackObject(
            url = url,
            title = title,
            artist = show_title,
            thumb = thumb,
            duration = duration
        ))

    return oc
