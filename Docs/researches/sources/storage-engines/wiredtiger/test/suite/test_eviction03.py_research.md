# sources/storage-engines/wiredtiger/test/suite/test_eviction03.py

## Purpose

Confirms obsolete time-window cleanup reduces the average on-disk page footprint after eviction rewrites pages.

## Important APIs, Types, and Functions

Defines `verify_dump_pages`, `derive_avg_disk_footprint`, and `test_eviction03`; inherits `eviction_util` and `suite_subprocess` to run `wt verify -d dump_pages`.

## Control Flow

The test creates three tables, populates timestamped data, checkpoints and closes, dumps page disk sizes, reopens with high obsolete time-window cleanup limits, advances oldest, evicts pages, reopens, dumps again, and compares average `dsk_mem_size` per table.

## State and Persistence Behavior

Persistence is the core signal: page images are measured before and after cleanup through the external `wt` utility. Timestamp advancement makes time-window metadata obsolete.

## Dependencies and Integration Points

Depends on diagnostic builds, `wiredtiger.diagnostic_build`, regex parsing, `statistics.mean`, `eviction_util`, and the `wt` subprocess wrapper.

## Risks and Maintenance Signals

The test skips non-diagnostic builds and relies on debug dump output format. Average size comparisons can be affected by page layout changes unrelated to time-window metadata.

## Test Signals

Signals are successful dump-page verification and average disk footprint strictly decreasing for every table.
