# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/fixed.h

This header defines libmad's fixed-point numeric model for the 9front build. It uses Plan 9 integer types (`u32int`, `vlong`) and defines `mad_fixed_t` as 32-bit signed fixed point with `MAD_F_FRACBITS == 28`. The representable range is approximately -8.0 to +8.0, with `MAD_F_ONE` as `0x10000000`.

The header provides conversion, integer/fraction extraction, add/subtract, and multiplication/scaling macros. It includes multiple architecture-specific multiplication implementations, including Intel inline assembly, ARM, MIPS, SPARC, PowerPC, 64-bit, and portable fallback paths. The active path depends on compile-time `FPM_*` and optimization flags. If neither an FPM mode nor fallback is selected, preprocessing fails.

Layer decoders and synthesis code rely on these macros for every scaling, requantization, IMDCT, windowing, and stereo operation. This file is performance-critical and assumes compiler support for the selected inline assembly/macros. It declares `mad_f_abs` and `mad_f_div`, implemented in `fixed.c`.
