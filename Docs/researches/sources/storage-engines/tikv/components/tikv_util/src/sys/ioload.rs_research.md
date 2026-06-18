# sources/storage-engines/tikv/components/tikv_util/src/sys/ioload.rs

## Purpose
Snapshots Linux block-device IO counters from `/sys/block/*/stat` into typed `IoLoad` structures.

## Important APIs, Types, and Functions
- `IoLoad` stores read/write IO counts, merges, sectors, ticks, in-flight, queue time, and optional discard counters.
- `IoLoad::snapshot()` returns a `HashMap<String, IoLoad>` on Unix; non-Unix returns an empty map in the cfg branch.

## Control Flow
The Unix snapshot walks `/sys/block/`, reads each `stat` file, parses whitespace-separated numbers into `f64`s with malformed values defaulting to zero, skips devices with fewer than 11 fields, and records optional discard fields when present.

## State and Persistence Behavior
The method returns a point-in-time map and stores no global state.

## Dependencies and Integration Points
Uses filesystem reads and `HashMap`. It is exported through `sys/mod.rs` for monitoring code that needs block-device load snapshots.

## Risks
Device names are inserted with `format!("{:?}", entry.file_name())`, which includes debug formatting rather than plain string conversion. Parse failures become zero values, potentially hiding malformed stats. The non-Unix signature references `NICLoad` in the unused cfg branch, which would matter only on non-Unix compilation.

## Test Signals
No local tests; expected behavior follows Linux block stat format documented in comments.
