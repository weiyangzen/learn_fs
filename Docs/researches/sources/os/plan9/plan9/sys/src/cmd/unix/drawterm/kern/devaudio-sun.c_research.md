# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devaudio-sun.c

Solaris/Sun `/dev/audio` backend for drawterm audio output and volume control.

Key responsibilities:
- Locates audio device from `AUDIODEV` or defaults to `/dev/audio`, deriving the control device by appending `ctl`.
- Opens playback and control file descriptors and configures 44.1 kHz, 16-bit, stereo, linear PCM playback.
- Detects host byte order and swaps Plan 9 little-endian samples on big-endian systems.
- Implements playback write loop, close, speed setting/getting, audio volume/balance setting/getting, and default treble/bass reporting.
- Converts between Plan 9 left/right percentages and Sun gain/balance values.

Important behavior:
- Only opens playback write-only; `audiodevread()` always errors `"no reading"`.
- `Vspeed` changes sample rate and stores the speed for later open/config calls.
- Volume updates preserve the side not explicitly set when passed a negative left or right value.

Dependencies:
- Depends on Solaris `<sys/audio.h>` and `AUDIO_SETINFO`/`AUDIO_GETINFO` ioctls.

Notable risks:
- Control device name is built by appending `ctl` to the audio path, matching Solaris conventions but not portable.
- Write errors call `oserror()` inside the loop; partial-write recovery is minimal.
