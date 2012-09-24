import re

BY5_VIDEO_PREFIX      = "/video/5by5"
BY5_MUSIC_PREFIX      = "/music/5by5"

TITLE = "5by5"
ICON = "icon-default.png"
ART = "art-default.jpg"

CACHE_INTERVAL = 1800

NAMESPACES = { 'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd', 'atom10': 'http://www.w3.org/2005/Atom' }

FEED_URL = 'http://feeds.feedburner.com/%s?format=xml'

AUDIO_FEEDS = [ 'back2work', 'bigwebshow', 'brieflyawesome', 'buildanalyze', 'contenttalks', 'criticalpath', 
                'dailyedition', '5by5-devshow', 'founderstalk', 'hypercritical', '5by5-ontheinternet',
                'PaleoPodcast', 'thepipelineshow', '5by5-superhero', 'thetalkshow']

VIDEO_FEEDS = [ 'bigwebshowvideo', 'brieflyawesomevideo', 'devshowvideo', 'thetalkshow-video']

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

    HTTP.CacheTime = CACHE_INTERVAL

####################################################################################################
@handler('/music/5by5', TITLE, art = ART, thumb = ICON)
def MainMenuMusic():
    oc = ObjectContainer()

    for channel in AUDIO_FEEDS:

        feed = XML.ElementFromURL(FEED_URL % channel)
        title = feed.xpath("//channel/title/text()", namespaces = NAMESPACES)[0]
        summary = feed.xpath("//channel/description/text()", namespaces = NAMESPACES)[0]
        thumb = feed.xpath("//channel/itunes:image", namespaces = NAMESPACES)[0].get('href')
        
        oc.add(DirectoryObject(key = 
            Callback(MusicChannelMenu, channel = channel, channel_title = title), 
            title = title,
            summary = summary,
            thumb = thumb))

    return oc

####################################################################################################
@handler('/video/5by5', TITLE, art = ART, thumb = ICON)
def MainMenuVideo():
    oc = ObjectContainer()

    for channel in VIDEO_FEEDS:

        feed = XML.ElementFromURL(FEED_URL % channel)
        title = feed.xpath("//channel/title/text()", namespaces = NAMESPACES)[0]
        summary = feed.xpath("//channel/description/text()", namespaces = NAMESPACES)[0]
        thumb = feed.xpath("//channel/itunes:image", namespaces = NAMESPACES)[0].get('href')
        
        oc.add(DirectoryObject(key = 
            Callback(VideoChannelMenu, channel = channel, channel_title = title), 
            title = title,
            summary = summary,
            thumb = thumb))

    return oc

####################################################################################################
@route('/music/5by5/{channel}', allow_sync = True)
def MusicChannelMenu(channel, channel_title):
    return ChannelMenu(channel, channel_title, False)

####################################################################################################
@route('/video/5by5/{channel}', allow_sync = True)
def VideoChannelMenu(channel, channel_title):
    return ChannelMenu(channel, channel_title, True)

####################################################################################################
def ChannelMenu(channel, channel_title, video = False):

    feed = XML.ElementFromURL(FEED_URL % channel)

    show_title = feed.xpath("//channel/title/text()", namespaces = NAMESPACES)[0]
    thumb = feed.xpath("//channel/itunes:image", namespaces = NAMESPACES)[0].get('href')

    oc = ObjectContainer(title2 = channel_title)

    for item in feed.xpath("//item", namespaces = NAMESPACES):
        title = item.xpath(".//title/text()", namespaces = NAMESPACES)[0]
        url = item.xpath(".//guid/text()", namespaces = NAMESPACES)[0]
        
        # [Optional]
        summary = None
        try: summary = item.xpath(".//description/text()", namespaces = NAMESPACES)[0]
        except: pass

        # The duration is in the format HH:MM:SS and therefore we must convert this into a suitable
        # number of milliseconds.
        duration_string = item.xpath(".//itunes:duration/text()", namespaces = NAMESPACES)[0]
        duration_dict = re.match("((?P<hours>[0-9]+):)?((?P<mins>[0-9]+):)?(?P<secs>[0-9]+)", duration_string).groupdict()
        
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
        
        if video:
            
            # The title's of video items allways end in "- Video", which is not really helpful, therefore we
            # will simply remove it.
            title = title.strip("- Video")

            oc.add(VideoClipObject(
                url = url + "#video",
                title = title,
                summary = summary,
                thumb = thumb,
                duration = duration
            ))

        else:
            oc.add(TrackObject(
                url = url,
                title = title,
                artist = show_title,
                thumb = thumb,
                duration = duration
            ))

    return oc