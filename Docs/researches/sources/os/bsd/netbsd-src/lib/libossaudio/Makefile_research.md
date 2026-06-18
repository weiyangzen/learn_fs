# File Research: sources/os/bsd/netbsd-src/lib/libossaudio/Makefile

Builds `libossaudio` with warning level 5. The library sources are OSS DSP/ioctl/capability handling plus OSSv3 and OSSv4 mixer/global compatibility files.

It installs `soundcard.h` into `/usr/include` and `ossaudio.3` as the manual page. The current directory is added to `CPPFLAGS` so internal includes resolve locally.
