# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devaudio-unix.c

Implements the Unix/BSD backend for drawterm audio using OSS-style `/dev/dsp` and `/dev/mixer`.

Key behavior:
- Opens `/dev/dsp` for output and `/dev/mixer` for mixer control.
- Configures 16-bit stereo output at 44100 Hz through `SNDCTL_DSP_*` ioctls.
- Maps Plan 9 volume IDs to OSS mixer IDs for audio, bass, treble, line, pcm, synth, cd, mic, and speaker.
- Implements volume get/set and speed get/set.
- Implements audio writes as a full-write loop.
- Does not implement recording; `audiodevread` always errors with `"no reading"`.

Dependencies:
- `devaudio.h` supplies the abstract audio operations and volume IDs.
- Uses host OSS headers: Linux `<linux/soundcard.h>` or BSD `<sys/soundcard.h>`.
- Reports host errors through `oserror()`.

Notable risks:
- The backend assumes legacy OSS devices exist.
- `audiodevsetvol` writes `-1` into one channel when the higher layer asks for left-only or right-only changes; the OSS packed mixer value path does not preserve the existing opposite channel.
