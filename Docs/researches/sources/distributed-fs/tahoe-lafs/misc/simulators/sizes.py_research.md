# sources/distributed-fs/tahoe-lafs/misc/simulators/sizes.py

## Purpose

This simulator estimates storage overhead and "alacrity" for several immutable-share block validation schemes across file sizes.

## Important APIs, Types, and Functions

`Args` parses mode and hash-tree arity. `Sizes` computes segment counts, share sizes, validation tree depth, storage overhead, transmission overhead, total overhead percentage, and bytes needed before some data can be validated. Modes are `alpha` (no block hash tree), `beta` (flat per-block hashes), and `gamma` (k-ary block hash tree). `fmt` formats sizes. `text` prints a table, while `graph` is an unfinished Gnuplot path.

## Control Flow

Direct execution calls `text`. It parses options, prints headers, generates file sizes by powers of two, constructs `Sizes` for each, and prints share size, overhead, k, depth, and alacrity. `charttest` is a separate gdchart experiment not used by default.

## State, Dependencies, Integration, Risks, and Tests

State is computed in memory and printed. Dependencies are Twisted `usage` and optional gdchart/Gnuplot for unused graphing helpers. Integration is design exploration for Tahoe validation overhead. Risks include Python 2 division semantics, `opt_arity` signature likely wrong for Twisted usage callbacks, unqualified `k` variable in gamma mode is assigned from `arity` but easy to misread, and no tests. Test signals should instantiate `Sizes` for known file sizes/modes, verify monotonic overhead, invalid mode errors, and formatting boundaries.
