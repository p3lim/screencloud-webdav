# ScreenCloud - WebDAV

This is a plugin that allow you to use any [WebDAV](https://en.wikipedia.org/wiki/WebDAV) server (such as OwnCloud/NextCloud) as a host for [ScreenCloud](https://screencloud.net/).

### Installation

Preferences -> Online Services -> More services -> Install from URL:

- <https://github.com/p3lim/screencloud-webdav/releases/download/1.0.0/packaged.zip>

### Settings

![](https://github.com/p3lim/screencloud-webdav/raw/master/screenshot.png)

- `URL` cannot be prefixed with schema, HTTPS if forced.
- `Public Host` is an optional forward-facing prefix URL, in cases where you'd upload to `upload.example.com` but link to `i.example.com`.
- `Name` can contain any normal ScreenCloud format, in addition to a randomized string `{rnd_N}`, where `N` is the length of that string.

### License

See [LICENSE.txt](https://github.com/p3lim/screencloud-webdav/blob/master/LICENSE.txt)

Icon made by [[Gregor Cresnar](https://www.flaticon.com/authors/gregor-cresnar)] from <www.flaticon.com> is licensed by [CC 3.0 BY](http://creativecommons.org/licenses/by/3.0/).
