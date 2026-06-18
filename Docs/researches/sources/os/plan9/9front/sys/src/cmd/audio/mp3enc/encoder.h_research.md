# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/encoder.h

This header defines core encoder constants and declares the one-frame MP3 encode function.

Key constants:
- Delay constants: `ENCDELAY`, `MDCTDELAY`, `FFTOFFSET`, `DECDELAY`.
- MPEG analysis dimensions: `SBLIMIT`, `CBANDS`, `SBPSY_l`, `SBPSY_s`, `SBMAX_l`, `SBMAX_s`.
- FFT dimensions: `BLKSIZE`, `HBLKSIZE`, `BLKSIZE_s`, `HBLKSIZE_s`.
- Block types: `NORM_TYPE`, `START_TYPE`, `SHORT_TYPE`, `STOP_TYPE`.
- Stereo mode extension constants: `MPG_MD_LR_LR`, `MPG_MD_LR_I`, `MPG_MD_MS_LR`, `MPG_MD_MS_I`.

Export:
- `lame_encode_mp3_frame(...)`

Dependencies and integration:
- Includes `machine.h` and `lame.h`.
- Used throughout encoder, psychoacoustic, FFT, MDCT, and analysis code.
- Delay constants are critical for frame buffering in `lame.c` and `encoder.c`.

Risks:
- Changing delay or FFT constants affects buffer sizing and alignment across many modules.
- Comments document historical uncertainty around exact encoder/decoder delay; code relies on the chosen constants.
