# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/audioio.h

This header defines the older Solaris audio device ioctl ABI and state structures. It covers stream configuration/state, device-wide state, encoding constants, port masks, feature masks, and classic `AUDIO_*` ioctls.

Key contents:
- `audio_prinfo_t`: per-playback or per-record stream state, including format, gain, port, buffer size, counters, pause/error/waiting/open/active flags.
- `audio_info_t`: combined playback/record state plus monitor gain, mute state, reference count, and hardware/software feature flags.
- Audio encoding constants including u-law, A-law, signed linear PCM, DVI ADPCM, and unsigned 8-bit linear.
- Gain, balance, channel count, precision, and input/output port constants.
- Feature masks `AUDIO_HWFEATURE_*` and `AUDIO_SWFEATURE_MIXER`.
- `AUDIO_INITINFO()` macro for initializing `audio_info_t` to ignored-field values.
- `audio_device_t` and ioctls `AUDIO_GETINFO`, `AUDIO_SETINFO`, `AUDIO_DRAIN`, `AUDIO_GETDEV`, `AUDIO_DIAG_LOOPBACK`.

Dependencies:
- Includes `sys/types.h`, `sys/types32.h`, `sys/time.h`, and `sys/ioccom.h`.
- C++ guarded with `extern "C"`.

Research notes:
- This is an externally visible device ABI; struct layout and ioctl encodings are compatibility-sensitive.
- `AUDIO_SETINFO` uses the `AUDIO_INITINFO` convention where initialized values are ignored.
