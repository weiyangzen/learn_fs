# File Research: sources/os/bsd/openbsd-src/sys/sys/audioio.h

Purpose: Defines public audio and mixer ioctl data structures, constants, and well-known control names.

Key contents:
- Audio mode bits distinguish playback and recording.
- `AUDIO_INITPAR()` initializes `audio_swpar` fields to all-ones.
- `struct audio_swpar` describes signedness, endian, sample size, alignment, sample rate, play/record channels, block count, and block frame rounding.
- `struct audio_status`, `audio_device_t`, and `struct audio_pos` expose device status, identity, and playback/record counters.
- Defines audio ioctls for device info, position, get/set parameters, start/stop, and status.
- Defines mixer level, device info, control structures, mixer ioctls, and many canonical mixer/control names.

Filesystem relevance:
- Used by vnode/device ioctl paths for audio character devices.
- Pledge/ioctl filtering and generic vnode ioctl dispatch may reference these ioctl interfaces.
