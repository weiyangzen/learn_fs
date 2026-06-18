# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zvmem2.c

## Purpose
Implements Level 2 local/global VM controls and garbage-collector control hooks.

## Public Surface
- Exported setters: `set_vm_threshold`, `set_vm_reclaim`.
- Registered operators: `.currentglobal`, `.gcheck`, `.setglobal`, and Level 2 `.vmreclaim`.

## Implementation Notes
- `.setglobal` switches allocation between global and local VM.
- `.currentglobal` reports whether current allocation space is not local.
- `gcheck`/`scheck` reports whether an object is not local.
- `set_vm_threshold` clamps threshold values, with `-1` choosing debug-dependent defaults, then applies to global and local spaces.
- `set_vm_reclaim` toggles GC reclamation across system/global/local spaces based on values `-2..0`.
- `.vmreclaim` supports only immediate GC requests by returning `e_VMreclaim` for values 1 or 2.

## Dependencies
Uses Ghostscript dual-memory spaces, VM-space attributes, and interpreter error signaling.

## Risks and Notes
- Operators are registered even for initial Level 1 because initialization needs them.
- `.vmreclaim` does not itself collect; it exits to the interpreter caller.
- Filesystem relevance: none.
