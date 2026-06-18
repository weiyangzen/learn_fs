# File Research: sources/os/bsd/netbsd-src/lib/libossaudio/oss_ioctl.c

Variadic ioctl replacement entry point. `_oss_ioctl` extracts the optional argument pointer and dispatches by ioctl group: `'P'` to DSP, `'M'` to OSSv3 mixer, `'X'` to OSSv4 mixer, `'Y'` to OSSv4 global metadata, and all others to the native `ioctl`.

This function is the runtime target of the `soundcard.h` `#define ioctl _oss_ioctl` compatibility mechanism.
