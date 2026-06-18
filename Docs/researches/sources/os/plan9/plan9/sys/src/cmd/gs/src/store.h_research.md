# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/store.h

Purpose: macro layer for assigning Ghostscript `ref` objects while preserving save/restore and local/global VM invariants.

Key contents:
- Defines fast `ref_assign` variants and save checks using `idmemory` masks.
- Provides `ref_save`, `ref_mark_new`, `ref_assign_new`, `ref_assign_old`, and related `_in` variants for explicit memory contexts.
- Adds debug fill patterns for unused ref fields under `DEBUG`.
- Defines constructors for scalar refs: booleans, integers, marks, nulls, operators, reals.
- Defines constructors for composite refs: arrays, strings, structs, and associative structs.

Dependencies: `ialloc.h`, `idosave.h`, ref/type macros from the interpreter object system.

Integration notes: used by the PostScript interpreter to make all object-slot writes visible to Ghostscript’s memory manager.

Risks: macro parameters are evaluated in assignment contexts; callers must avoid expressions with unintended side effects. Correct use of `_new` versus `_old` variants is critical for VM save/restore correctness.
