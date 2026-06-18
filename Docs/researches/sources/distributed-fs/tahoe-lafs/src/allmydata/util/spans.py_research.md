# sources/distributed-fs/tahoe-lafs/src/allmydata/util/spans.py

## Purpose

This module represents sparse byte ranges and sparse byte data. `Spans` is a compressed integer-set optimized for range operations, while `DataSpans` stores non-overlapping byte chunks with offsets. Downloaders use these structures to track requested, received, and missing share bytes.

## APIs and control flow

`Spans` stores sorted `(start, length)` intervals. `add()` merges overlapping or adjacent ranges; `remove()` trims, deletes, or splits ranges; arithmetic operators implement union, subtraction, in-place updates, and intersection; `__contains__` checks full containment of a range. `overlap()` and `adjacent()` are shared helpers.

`DataSpans` stores sorted `(start, data)` chunks. `add()` overlays new data across existing spans, replacing overlaps and merging adjacent chunks. `get()` returns exact data only if the requested range is fully contained in one merged chunk. `remove()` deletes or splits data chunks, and `pop()` combines get/remove.

## State, dependencies, risks, and tests

State is in-memory interval lists and byte chunks. There are no external dependencies. Integration is downloader scheduling and remote-share data assembly.

Risks include O(n) operations on many small ranges, assertions for invalid ranges, subtle off-by-one errors when trimming/splitting, and `DataSpans.get()` requiring a single containing span. Test signals should cover adjacent merges, overlapping additions, left/right/middle removals, intersection, containment, empty spans, data overlay cases A-E described in comments, pop behavior, and invariant checks after every mutation.
