# File Research: sources/os/plan9/9front/sys/src/cmd/audio/zuke/icy.c

HTTP ICY/Shoutcast stream helper for zuke.

Key responsibilities:
- Opens an HTTP stream with `Icy-MetaData: 1`.
- Follows up to 10 `Location:` redirects.
- Reads ICY response headers, populating title/artist metadata for playlist generation or sending initial title updates.
- Parses `icy-metaint` and strips metadata blocks from the audio stream.
- Writes audio bytes to an output fd while sending `StreamTitle` updates over a channel.
- Runs the stream puller in a separate proc and closes the title channel on EOF/error.

Dependencies:
- Uses Plan 9 networking (`dial`, `netmkaddr`), `Biobuf`, threads/channels, and zuke `Meta`.

Research notes:
- Only plain HTTP URLs are handled; the code rewrites host/port into Plan 9 network addresses.
- Metadata parsing specifically looks for `StreamTitle='...';`.
