# File Research: sources/os/bsd/netbsd-src/lib/libossaudio/oss3_mixer.c

Implements OSSv3 mixer ioctl compatibility. `_oss3_mixer_ioctl` maps legacy mixer info, recsrc, masks, stereo masks, capabilities, and per-device volume reads/writes onto NetBSD `AUDIO_GETDEV`, `AUDIO_MIXER_DEVINFO`, `AUDIO_MIXER_READ`, and `AUDIO_MIXER_WRITE`.

`getdevinfo` caches mixer topology per device, maps NetBSD mixer labels to OSS mixer slots, records stereo-capable controls, and discovers the recording source control. Helpers translate between NetBSD enum/set opaque values and cached mixer indices.

Limits: only the first 64 NetBSD mixer controls are represented. Unknown or unmapped OSS mixer controls fail with `EINVAL`.
