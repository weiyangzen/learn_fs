# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/newmdct.h

## Scope
Header for the MDCT/subband transform implementation.

## API
Declares `mdct_sub48(lame_internal_flags *gfc, const sample_t *w0, const sample_t *w1, FLOAT8 mdct_freq[2][2][576])`.

## Dependencies
Requires prior declarations of `lame_internal_flags`, `sample_t`, and `FLOAT8`, typically through internal LAME headers.

## Risks and Notes
Guarded header, but not self-contained.
