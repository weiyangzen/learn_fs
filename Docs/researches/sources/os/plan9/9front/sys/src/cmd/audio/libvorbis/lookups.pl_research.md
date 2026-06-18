# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/lookups.pl

Perl generator for `lookup_data.h`.

Important behavior:
- Prints the libvorbis lookup-data header prologue.
- Generates float cosine, inverse-square-root, exponent, and dB conversion tables.
- Generates integer inverse-square-root and cosine tables for `INT_LOOKUP`.
- Uses fixed table sizes and shifts matching `lookup.c`: cosine size 128, inverse-square-root size 32, exponent range -32..32, dB table sizes/shifts, integer lookup shifts 10 and 9.

Integration points:
- Source of truth for generated lookup tables in `lookup_data.h`.
- Not used at runtime.

Risk and review signals:
- Generated header from this script differs slightly from the checked-in header style, including older copyright text and non-`const` declarations in the generator output.
- The generated guard also lacks a `#define`, matching the checked-in file’s ineffective guard.
- Re-running the script could cause formatting and constness churn.

Filesystem relevance:
- No filesystem logic. It is a build-time/codegen helper for audio math tables.
