# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iutil.h

Purpose: declares the interpreter utility functions implemented in `iutil.c`.

The interface covers:
- Ref copying/filling and object equality/identity.
- Name/string data extraction and printable conversion (`obj_cvp`, `obj_cvs`).
- Array and packed-array element extraction.
- VM-space interval checking.
- C string/ref string conversion.
- Numeric operand extraction and real/float creation.
- Matrix read/write helpers, including macros for new-array and save-aware writes.

The comments document precision caveats for float conversions and the special return behavior of printable conversion routines.
