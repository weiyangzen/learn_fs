# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/psymodel.h

This header declares the psychoacoustic analysis API used by the frame encoder.

Exports:
- `L3psycho_anal(...)`: classic psychoacoustic analysis.
- `L3psycho_anal_ns(...)`: nspsytune psychoacoustic analysis.
- `psymodel_init(lame_global_flags *gfp)`: initializes psychoacoustic internal state.

Dependencies:
- Includes `l3side.h` for `III_psy_ratio`, `lame_global_flags`, `sample_t`, and numeric typedefs.

Integration:
- Included by `encoder.c` to choose and call the psychoacoustic model before quantization.
- Implemented by `psymodel.c`.

Risks and edge cases:
- The `ener` parameter is declared as `FLOAT8 ener[2]`, but `psymodel.c` accepts and writes a 4-element energy array for L/R/M/S channels. Because C array bounds in parameters decay to pointers, this compiles, but the declaration under-documents the required storage.
- The first parameter is named `gfc` in declarations but is actually a `lame_global_flags *`; this is cosmetic but confusing because `gfc` usually means `lame_internal_flags *`.
