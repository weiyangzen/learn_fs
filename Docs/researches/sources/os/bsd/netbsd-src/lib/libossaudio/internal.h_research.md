# File Research: sources/os/bsd/netbsd-src/lib/libossaudio/internal.h

Private libossaudio header. It includes `soundcard.h`, undoes the public `ioctl` macro, and declares the hidden dispatcher functions used by `_oss_ioctl`.

It centralizes OSS/NetBSD volume conversion, integer ioctl argument access, OSS device-number extraction, and hidden symbol visibility. Implementations use these helpers to translate OSS requests to NetBSD audio ioctls.
