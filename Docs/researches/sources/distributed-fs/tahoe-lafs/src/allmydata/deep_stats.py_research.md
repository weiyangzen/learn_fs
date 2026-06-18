# sources/distributed-fs/tahoe-lafs/src/allmydata/deep_stats.py

## Purpose

This module implements deep traversal statistics for Tahoe directory trees, producing counters and histograms for files, directories, unknown nodes, and aggregate sizes.

## Important APIs, Types, And Functions

`DeepStats` has `API_VERSION = 1`. The constructor initializes counters, histograms, bucket state, and root `sqrt(10)` growth. `set_monitor()` attaches a monitor and initial status. `add_node()` classifies nodes as unknown, directory, mutable file, immutable file, or literal file and updates counters and histograms. `enter_directory()` records directory byte size and child count. `add()`, `max()`, `which_bucket()`, `histogram()`, `get_results()`, and `finish()` support aggregation.

## Control Flow

Directory traversal code calls `add_node()` for each reachable node and `enter_directory()` for directory contents. Immutable file sizes are bucketed and counted as literal or immutable CHK based on URI parsing. `get_results()` copies counters and renders histogram buckets into sorted `(min, max, count)` tuples.

## State And Persistence

State is in-memory counters, histograms, dynamic bucket list, monitor reference, and origin node. Results are consumed by web/API/CLI code but not persisted here.

## Dependencies And Integration Points

It depends on Tahoe node interfaces, `UnknownNode`, `LiteralFileURI`, URI parsing, and math utilities. It is used by `dirnode.DeepChecker`, `ManifestWalker`, and deep-stats API surfaces.

## Risks

Mutable file sizes are not counted, with TODO comments for servermap/size support. `which_bucket()` mutates the bucket list as sizes grow. URI parsing in `add_node()` can raise if an immutable node returns an unexpected URI. `set_monitor()` assumes the monitor accepts arbitrary attributes and status objects.

## Test Signals

Traverse synthetic trees with directories, CHK files, LIT files, mutable files, and unknown nodes; verify counters, largest values, histogram bucket boundaries, and monitor status updates.
