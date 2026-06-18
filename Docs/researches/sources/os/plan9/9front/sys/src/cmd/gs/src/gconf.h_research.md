# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gconf.h

## Scope

Wrapper for including the generated Ghostscript configuration header.

## Key Behavior

- Includes `gconfig.h` by default.
- If `GCONFIG_H` is defined, includes the header named by that macro.
- Intentionally has no include guard because it is included repeatedly with different macro definitions.

## Dependencies

Depends on either `gconfig.h` or a build-provided alternate config header.

## Risks And Invariants

- Adding double-inclusion protection would break `gconf.c` / generated-table macro expansion.
- Supports preprocessors that do not implement non-quoted include arguments unless `GCONFIG_H` is used.
