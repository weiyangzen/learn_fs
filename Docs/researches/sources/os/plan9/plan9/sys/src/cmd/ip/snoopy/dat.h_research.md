# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/dat.h

Core data model for `snoopy` protocol decoding and filtering.

Key contents:
- Network byte-order helper macros `NetS`, `Net3`, and `NetL`.
- `Proto`: protocol module callbacks for compile/filter/format, mux table, fields, and framer.
- `Mux`: maps protocol values to next protocol names and resolved `Proto*`.
- `Field`: filterable field metadata.
- `Msg`: mutable packet walk state and output buffer state.
- `Filter`: parsed filter AST node plus compiled protocol-specific comparison data.
- Declares shared parser/compiler/demux/framer APIs and global flags.

Integration:
- Included by every `snoopy` module.
- Used by yacc grammar and main filter optimizer.

Risks and notes:
- `Filter` stores numeric, vlong, and byte-array values in a union; field compile code must choose the right member consistently.
