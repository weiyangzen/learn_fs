# File Research: sources/os/plan9/9front/sys/src/cmd/audio/sundec/sundec.c

Sun/NeXT `.snd`/AU audio header decoder that delegates payload conversion to `pcmconv`.

Key responsibilities:
- Reads big-endian AU magic, data offset, length, encoding, sample rate, and channel count.
- Maps supported AU encoding codes to Plan 9 PCM descriptor fragments.
- Skips annotation/header padding before audio data.
- Executes `/bin/audio/pcmconv -i fmt`, optionally with `-l len` when data length is known.

Dependencies:
- Uses `/bin/audio/pcmconv` for actual sample conversion.

Research notes:
- Supports u-law, A-law, signed integer PCM widths, and float encodings listed in `fmttab`.
- Unknown or malformed encodings terminate with `sysfatal`.
