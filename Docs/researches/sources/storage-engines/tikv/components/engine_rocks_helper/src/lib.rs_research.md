<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks_helper/src/lib.rs -->
# sources/storage-engines/tikv/components/engine_rocks_helper/src/lib.rs

## Purpose
`lib.rs` is the crate root for `engine_rocks_helper`. It exposes SST recovery functionality while keeping helper metrics private to the crate.

## Important APIs, Types, and Functions
It declares `mod metric;` and `pub mod sst_recovery;`.

## Control Flow
There is no runtime control flow. Module visibility controls external API: users can access `sst_recovery`, while metrics are used internally by that module.

## State and Persistence Behavior
No state is stored in the crate root.

## Dependencies and Integration Points
External users integrate with `engine_rocks_helper::sst_recovery`. The private `metric` module is referenced by `sst_recovery.rs`.

## Risks and Edge Cases
Adding more helper modules requires consciously choosing public versus crate-private visibility. Keeping metrics private avoids making metric symbols part of the external helper API.

## Test Signals
Compilation verifies module wiring; `sst_recovery` tests verify the public module.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks_helper/src/lib.rs -->
