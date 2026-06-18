# sources/distributed-fs/tahoe-lafs/misc/simulators/ringsim.py

## Purpose

This simulator compares Tahoe share placement on a simple ring versus per-file permuted peer lists, tracking usage spread and the point where servers fill or uploads wrap.

## Important APIs, Types, and Functions

`abbreviate_space` formats byte counts. `make_up_a_file_size` deterministically maps seeds to exponential file sizes using MD5. `Server` tracks node ID, capacity, used bytes, share count, and first-full tick. `Ring` builds sorted servers, returns either permuted or linear server order for a storage index, and reports usage distribution. `Options` parses k/N, server count, seeds, and permute flag. `do_run` performs uploads until the grid is full; `do_ring` prints expected upload count and initializes the ring.

## Control Flow

A global sample computes average file size. The run creates a ring, then for each generated file computes storage index, file size, share size, and server order. It tries to place `N` shares, skipping full servers and wrapping as needed. It reports first full server, first wrapped file, periodic usage stats, and final grid-full state.

## State, Dependencies, Integration, Risks, and Tests

State is simulated server usage only. Dependencies are Twisted `usage`, MD5, and deterministic seeds. Integration is design discussion for share placement behavior. Risks include Python 3 bytes/string hashing errors, integer division differences, fixed 1 TB capacity, and no direct return metrics except printed output. Tests should use small server counts/capacities, deterministic seeds, permuted vs linear orders, and full-grid termination.
