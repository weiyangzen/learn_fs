# File Research: sources/os/plan9/9front/sys/src/cmd/xd.c

Hex/octal/decimal/ascii dump utility with configurable address base, data width, endian order, repeat elision, and multiple output formats.

Key behavior:
- Global flags select little-endian assembly (`-s`), unbuffered input flush behavior (`-u`), repeat-line elision (`-r`), and address base (`-a{odx}`).
- Format options select character output or 1/2/4/8-byte numeric groups in octal, decimal, or hex.
- `xd()` reads 16-byte blocks, zero-pads partial final blocks for formatting, elides repeated full blocks when requested, and prints final address after short block.
- `fmt0`/`fmt1`/`fmt2`/`fmt3` assemble and print values of different widths; `fmtc()` prints printable characters or escapes/control numeric forms.
- `flushout()` flushes stdout before blocking for more input when `-u` is used.

Notable dependencies:
- Plan 9 Bio and formatted printing.

Research notes:
- Up to 9 explicit formats are allowed because `initarg()` exits once `narg >= Narg` after increment.
- The big-endian 8-byte assembly path uses explicit 32-bit halves.
