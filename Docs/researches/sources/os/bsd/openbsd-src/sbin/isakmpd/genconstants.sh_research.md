# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/genconstants.sh

Shell/awk generator that converts a `.cst` constants specification into a generated header and C file.

Generated header:
- Include guard based on the basename.
- Includes `constants.h`.
- Emits `extern struct constant_map <prefix>_cst[];`.
- Emits `#define PREFIX_NAME value` for indented constant rows.

Generated C:
- Includes `constants.h` and the generated header.
- Emits `struct constant_map <prefix>_cst[] = { ... }`.
- Adds a `{ 0, 0 }` terminator at `.` section boundaries.
- Stores optional linked-map values from a third field.

It uses `${AWK:-awk}` and an awk `locase()` helper implemented by shelling out to `tr`.
