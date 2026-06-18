# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_spans.py

## Purpose
This module tests `allmydata.util.spans.Spans`, `overlap`, and `DataSpans`. These utilities model byte ranges and sparse byte data, so the tests focus on range algebra, containment, length accounting, chunk retrieval, mutation, copying, and randomized equivalence to simple reference implementations.

## Important APIs, Types, And Functions
`sha256(data)` returns deterministic hex bytes and is used as a pseudo-random generator. `SimpleSpans` is a deliberately inefficient oracle backed by a set of byte offsets; it implements `add`, `remove`, `each`, iteration as coalesced `(start, length)` ranges, `len`, boolean state, `+`, `-`, `+=`, `-=`, `&`, and containment of full spans. `ByteSpans` compares this oracle to the production `Spans`.

`extend` and `replace` are helper functions for the data-span oracle. `SimpleDataSpans` represents sparse data with a missing-mask string and a byte buffer; it implements `get_chunks`, `get_spans`, `get`, `pop`, `remove`, and `add`. `StringSpans` applies the same behavioral checks to the simple oracle and production `DataSpans`.

## Control Flow
`ByteSpans.test_basic` checks empty spans, construction from start/length and from another span set, mutation chaining, containment semantics, iteration, and length. `test_large` validates huge spans such as `2**65` without expanding them, proving the production representation is interval-based. `test_math` exercises subtraction, intersection, union, and in-place variants over overlapping, adjacent, and disjoint ranges.

`test_random` executes 1000 deterministic operations derived from SHA-256 bytes. It repeatedly resets, constructs, adds, removes, unions, subtracts, mutates in place, intersects, and then compares the oracle and production object on expanded offsets, total length, truthiness, coalesced spans, and sampled containment. `test_overlap` exhaustively checks small range pairs by comparing `overlap(a,b,c,d)` to set intersection.

For data spans, `do_basic` checks empty behavior, gap handling, copy independence, chunk totals, partial pop/removal, overlapping writes, and data replacement. `do_scan` builds a baseline with many gaps and then tests every added interval and many short removals, checking both retrieval correctness and absence/presence of bytes. `StringSpans.test_random` performs 1000 deterministic add/remove/pop operations and compares `DataSpans` to `SimpleDataSpans` over length, dump positions, and 100 sampled reads per step.

## State And Persistence Behavior
The tests are pure in-memory checks. `Spans` state is a set of covered byte ranges and must maintain canonical coalesced iteration while supporting very large lengths. `DataSpans` state is sparse byte content; adding data fills or overwrites ranges, removing creates holes, and popping returns data only for fully available requested ranges while removing it. Copy constructors must preserve data but not alias mutable state.

## Dependencies And Integration Points
The module depends on Twisted Trial and `allmydata.util.spans`. In Tahoe-LAFS, span utilities are typically used by transfer, encoding, repair, and download code that needs compact accounting for byte ranges or sparse data. These tests therefore provide low-level confidence for higher-level file-transfer correctness without using network or filesystem fixtures.

## Risks And Edge Cases
Important edge cases include huge non-expanded ranges, zero or empty states, adjacent range coalescing, partial overlap math, full-span containment semantics, sparse reads that cross holes, overlapping writes replacing old data, copy independence, and deterministic randomized operations that could hide gaps if the oracle shares the same bug. The reference implementations are intentionally simple and structurally different, reducing that risk.

## Test Signals
Passing tests signal that `Spans` correctly implements range algebra and accounting, `overlap` returns exact intersections or `None`, and `DataSpans` preserves sparse byte data semantics under add/remove/pop/copy operations. The randomized oracle comparisons are the strongest signal because they cover many operation sequences beyond handwritten examples.
