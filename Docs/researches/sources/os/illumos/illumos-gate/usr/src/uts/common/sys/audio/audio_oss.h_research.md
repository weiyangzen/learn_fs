# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/audio/audio_oss.h

This header defines the illumos/Solaris OSS compatibility ABI for `/dev/dsp` and `/dev/mixer`. It is primarily a public ioctl and constant definition file, with many entries retained for source compatibility with OSS applications even where Solaris does not implement the behavior.

Key contents:
- OSS buffer, pointer, sync, error, digital control, system info, mixer extension, audio info, mixer info, and card info structs.
- OSS ioctl encoding macros: `OSSIOC_*`, `__OSSIO*`.
- Global OSS4-style ioctl commands such as `SNDCTL_SYSINFO`, `SNDCTL_AUDIOINFO`, `SNDCTL_MIX_*`, `SNDCTL_DSP_*`.
- Legacy OSS mixer constants and source compatibility macros such as `SOUND_MIXER_*`, `SOUND_MASK_*`, and `MIXER_READ/WRITE`.
- Audio format masks `AFMT_*`, native/opposite endian aliases, PCM capability masks, trigger masks, channel binding masks, and internal `SNDCTL_SUN_SEND_NUMBER`.

Dependencies:
- Includes `sys/types.h` and `sys/time.h`.
- C++ guarded with `extern "C"`.

Research notes:
- The file is ABI-sensitive: struct sizes, ioctl numbers, and constant values are externally visible.
- Comments explicitly warn that many definitions are compatibility-only or obsolete.
- `SNDCTL_SUN_SEND_NUMBER` is duplicated with `sys/audioio.h` and marked internal.
