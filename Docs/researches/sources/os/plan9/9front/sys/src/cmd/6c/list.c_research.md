# File Research: sources/os/plan9/9front/sys/src/cmd/6c/list.c

- Role: Debug/listing formatter registration and conversion routines for 6c amd64 assembly IR.
- `listinit()` installs Plan 9 `Fmt` handlers for `%A`, `%B`, `%P`, `%S`, `%D`, and `%R`.
- `Pconv()` formats `Prog` records, with special forms for `ADATA` and `ATEXT` that include width/frame scale fields.
- `Dconv()` formats `Adr` operands: registers, indirect register addressing, branches relative to `pc`, extern/static/auto/param symbols, constants, floats, strings, and address constants.
- `Rconv()` maps amd64 register address enum values to textual register names, including byte, general, x87, MMX, XMM, segment, descriptor, control, debug, and task registers.
- `Sconv()` escapes fixed-size string constants for printable assembly output.
- Dependency: relies on global `pc`, `var[]`, `anames[]`, and register enum layout from `6.out.h`.
