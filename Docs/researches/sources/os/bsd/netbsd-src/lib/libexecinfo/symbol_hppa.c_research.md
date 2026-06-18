# File Research: sources/os/bsd/netbsd-src/lib/libexecinfo/symbol_hppa.c

## Purpose
HPPA-specific function descriptor canonicalization for `libexecinfo`.

## Main Components
- Defines HPPA plabel detection and pointer masking macros.
- Defines `hppa_plabel` with program-counter and static-link fields.
- `symbol_canonicalize_md()` returns the plabel program counter when the input address is a plabel, otherwise returns the address as-is.

## Integration
Conditionally built by the Makefile when `symbol_hppa.c` matches the target machine architecture.

## Risks / Notes
Correctness depends on HPPA plabel bit conventions and descriptor layout.
