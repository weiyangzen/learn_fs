# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/istack.h

Purpose: declares the expandable ref-stack representation and procedural API.

Important types:
- `ref_stack_block` overlays the leading refs of each stack block with `next` and `used` array refs.
- `ref_stack_enum_t` supports top-to-bottom enumeration across stack blocks.

Important API groups:
- Initialization and configuration: init, expansion flag, error codes, max count, margin.
- Inspection: count, max count, index, count-to-mark.
- Store/copy: store checks and stack-to-array copy with optional save/undo handling.
- Mutation: pop, clear, pop-to-depth, pop-block, extend, push.
- GC/lifecycle: enumerate, cleanup, release, free.

The header documents the invariant that stack-related underflow/overflow recovery is handled by top-level interpreter error recovery, with special stack-specific wrappers elsewhere.
