# sources/distributed-fs/tahoe-lafs/misc/simulators/bench_spans.py

## Purpose

This benchmark replays recorded `DataSpans` operation traces and measures microsecond-level performance for increasing operation counts.

## Important APIs, Types, and Functions

Regex constants recognize `.get`, `.pop`, `.remove`, and `.add` trace lines; string constants recognize `.dump`, `.get_spans`, and initialization. Class `B` holds an input file and `DataSpans` instance. `B.init` resets state. `B.run(N)` reads up to `N` trace lines and invokes matching `DataSpans` methods.

## Control Flow

The script prints a benchmark footer/header, then for `N` values 600, 6000, and 60000 opens the trace file, creates `B`, and calls `benchutil.rep_bench` with `B.run` and `B.init`.

## State, Dependencies, Integration, Risks, and Tests

State is in-memory `DataSpans` mutation during replay. Dependencies are `pyutil.benchutil`, Tahoe `DataSpans`, regex trace format, and Python 2 `"rU"`. Risks include warning noise for unrecognized lines, replaying only a prefix for each benchmark, no validation of operation results, and allocating `'x' * length`. Tests should use tiny trace fixtures for every operation and assert calls on a fake spans object.
