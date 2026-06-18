# sources/distributed-fs/tahoe-lafs/misc/simulators/count_dirs.py

## Purpose

This estimator scans a native directory tree and approximates Tahoe directory metadata storage overhead under several hypothetical directory encoding modes.

## Important APIs, Types, and Functions

Constants `URI_SIZE` and `SLOTNAME_SIZE` model encoded targets. `slotsize(mode, numfiles, numdirs)` computes per-directory metadata size for modes `A`, `B1`, `B2`, `C1`, and `C2`. `scan(root)` walks the filesystem, adds filename string sizes and slot sizes, and prints totals.

## Control Flow

For each directory visited by `os.walk`, the script counts files/subdirs, adds joined filename lengths, accumulates all mode totals, then prints directory count, file count, and bytes per mode. Direct execution scans `sys.argv[1]`.

## State, Dependencies, Integration, Risks, and Tests

State is read-only filesystem traversal and in-memory counters. Integration is design exploration for Tahoe directory formats. Risks include approximate constants, no handling for filename encoding length versus Python string length, following `os.walk` defaults, and no argument validation. Tests should construct small directory trees and verify per-mode arithmetic for known file/subdir counts.
