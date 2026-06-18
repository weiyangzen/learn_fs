# File Research: sources/os/plan9/9front/sys/src/cmd/strip.c

`strip.c` removes symbol/debug tail data from recognized Plan 9 executable binaries.

Key behavior:
- Usage supports in-place stripping of one or more files, or `-o ofile file` for one output file.
- Uses `crackhdr` from `<mach.h>` to identify executable header and text/data layout.
- Accepts magic values in Plan 9 `_MAGIC` ranges.
- Computes stripped length as `fhdr.datoff + fhdr.datsz`.
- Reads exactly that prefix, zeroes `Exec` fields `syms`, `spsz`, and `pcsz`, then writes it back.
- In-place mode removes the original before recreating it with the original mode.

Error handling:
- `error` formats to stderr without immediate exit; `strip` returns status per file.
- Already stripped files are reported but not treated as fatal in in-place mode.

Risks:
- In-place remove-then-create can lose the original if create/write fails after removal.
- Assumes the executable header begins with `Exec` and that zeroing those fields is correct for recognized formats.
