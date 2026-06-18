# File Research: sources/os/bsd/netbsd-src/lib/libossaudio/oss_caps.c

Computes OSS PCM capability bits from NetBSD audio device properties. `_oss_get_caps` always advertises trigger, multi-open, and free-rate support, then adds channel preference and duplex/MMAP/input/output bits based on `AUDIO_GETPROPS` and `AUDIO_GETFORMAT`.

The result is returned through the caller-provided integer pointer and errors propagate from underlying audio ioctls.
