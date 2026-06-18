# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/version.c

LAME version-string and numerical-version implementation.

Key responsibilities:
- Stringifies version macros from `version.h`.
- Builds full and short LAME version strings, including alpha/beta/date and compile-time feature markers where applicable.
- Provides GPSYCHO and mp3x version strings.
- Returns the LAME project URL.
- Fills `lame_version_t` with LAME and psychoacoustic model version numbers plus compile-time feature text.

Dependencies:
- Includes public `lame.h` and local `version.h`.

Research notes:
- Full alpha/beta version strings may include compile date/time, while short versions avoid date/time for output validation stability.
- Compile-time feature suffixes come from `MMX_choose_table`, `KLEMM`, and `RH`.
