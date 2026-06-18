<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat.h -->
# sources/test-tools/strace/src/xlat.h

Purpose: Public xlat table ABI: table kinds, style/format flags, `struct xlat_data`, `struct xlat`, and initializer macros for generated tables.

Important APIs/types/functions:
- Direct includes: `<stdint.h>`
- Local/exported macros: `STRACE_XLAT_H`, `XLAT_STYLE_FORMAT_SHIFT`, `XLAT_STYLE_VERBOSITY_MASK`, `XLAT_STYLE_FORMAT_MASK`, `XLAT_STYLE_SPEC_BITS`, `XLAT_STYLE_MASK`, `XLAT`, `XLAT_PAIR`, `XLAT_TYPE`, `XLAT_TYPE_PAIR`

Control flow:
- control flow is linear around a small decoder/helper surface and returns standard strace `RVAL_*` flags

State and persistence behavior:
- no persistent storage; behavior is derived from current tracee arguments, return value, and build-time headers

Dependencies and integration points:
- depends on strace `defs.h` formatting/fetch APIs and listed kernel/libc headers

Risks:
- length/count fields need bounds-aware printing to avoid misleading output or excessive tracee reads

Test signals:
- compile coverage plus targeted decoder-output fixtures are the primary validation signal
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat.h -->
