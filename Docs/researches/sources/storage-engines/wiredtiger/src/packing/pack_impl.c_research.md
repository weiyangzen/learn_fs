<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/packing/pack_impl.c -->
# sources/storage-engines/wiredtiger/src/packing/pack_impl.c

## Purpose
Implements internal non-streaming struct packing helpers and format validation wrappers.

## Important APIs, Types, and Functions
`__struct_check`, `__wt_struct_confchk`, `__wt_struct_size`, `__wt_struct_pack`, `__wt_struct_unpack`, and `__wt_struct_repack`.

## Control Flow
Format checking initializes a `WT_PACK`, iterates `__pack_next` until not found, and optionally reports fixed-size bitfield status for empty or single `t` formats. Pack/size/unpack/repack functions wrap varargs and delegate to `__wt_struct_*v` or repack implementation.

## State and Persistence Behavior
No persistent state. Output buffers are filled according to format definitions, and validation results guide configuration acceptance.

## Dependencies and Integration Points
Depends on the lower-level pack parser/read/write implementation and configuration validation paths.

## Risks and Edge Cases
Format parser changes can affect both data encoding and config validation. Fixed-bitfield detection only recognizes the narrow empty/single-`t` cases.

## Test Signals
Format validation tests, fixed-bitfield config cases, size/pack/unpack round trips, and repack compatibility tests are useful.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/packing/pack_impl.c -->
