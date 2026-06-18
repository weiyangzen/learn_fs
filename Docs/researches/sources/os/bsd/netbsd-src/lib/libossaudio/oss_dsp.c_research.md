# File Research: sources/os/bsd/netbsd-src/lib/libossaudio/oss_dsp.c

Main OSS DSP ioctl compatibility dispatcher. `_oss_dsp_ioctl` translates reset/sync, speed, stereo/channels, block sizing, fragments, supported formats, buffer-space queries, nonblocking mode, capabilities, triggers, input/output pointers, play/record volume, duplex, delay, and target/source names onto NetBSD audio ioctls.

Format conversion helpers map OSS `AFMT_*` values to NetBSD encodings/precision and back. Channel negotiation falls back to hardware format if the requested count is invalid, matching OSS expectations that a reasonable value is returned.

It tracks underrun/overrun counters across calls for OSS relative error reporting. Several OSS calls are intentionally unsupported and return `EINVAL`, including filters, skip/silence, mmap buffer descriptors, and syncro.
