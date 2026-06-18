# File Research: sources/os/plan9/plan9/sys/src/cmd/vc/list.c

Purpose: debug/listing formatters for backend instructions, addresses, symbols, strings, and bitsets.

Key functions:
- `listinit` installs format verbs.
- `Bconv` formats variable bitsets using `var[]`.
- `Pconv` formats `Prog` instructions with special cases for `DATA` and `TEXT`.
- `Aconv` maps opcode integers through `anames`.
- `Dconv` formats `Adr` operands by addressing type.
- `Sconv` quotes fixed-size string constants.
- `Nconv` formats named address components such as extern, static, auto, and param.

Integration points:
- Used by debug flags throughout `cgen.c`, `reg.c`, `peep.c`, and `txt.c`.
- Depends on `anames[]` from `enam.c`.

Risks:
- Fixed-size buffers (`STRINGSZ`) are used with length checks in some but not all formatting paths.
- Debug output correctness depends on address enum consistency.
