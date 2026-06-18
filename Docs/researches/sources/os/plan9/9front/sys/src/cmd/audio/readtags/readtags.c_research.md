# File Research: sources/os/plan9/9front/sys/src/cmd/audio/readtags/readtags.c

Audio metadata inspection command with optional embedded image extraction/display.

Key responsibilities:
- Uses libtags `tagsget()` with custom read/seek callbacks over stdin or file paths.
- Prints known tags such as artist, album, title, date, track, replaygain, genre, composer, comment, albumartist, and image metadata.
- Prints duration, sample rate, channel count, and bitrate when available.
- With `-i`, extracts the first embedded JPEG/PNG image, optionally runs its special tag reader, and pipes it into `jpg -9t` or `png -9t`.

Dependencies:
- Uses Plan 9 `tags.h`, subprocess creation through `rfork`, and image decoder commands.

Research notes:
- Unknown tags print their original key.
- `-i` exits with an error if no image is found.
