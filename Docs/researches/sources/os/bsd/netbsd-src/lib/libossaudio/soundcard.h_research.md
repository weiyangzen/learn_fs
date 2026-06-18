# File Research: sources/os/bsd/netbsd-src/lib/libossaudio/soundcard.h

Public OSS compatibility header. It warns new code to use NetBSD `<sys/audioio.h>`, then defines OSS DSP, mixer, and OSSv4 ioctl numbers, audio formats, PCM/DSP capabilities, trigger bits, channel-order constants, aliases, and all compatibility structures.

The header includes endian-specific native-format aliases, OSSv3 mixer constants and masks, DSP buffer/counter structures, OSSv4 system/audio/card/mixer/control structures, and no-op OSSv4 song/name/label ioctls.

At the end it redefines `ioctl` to `_oss_ioctl` and arranges the prototype depending on whether `<sys/ioctl.h>` was already included. Including this header therefore opts callers into libossaudio translation.
