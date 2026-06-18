# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/copy.c

Purpose: recursively copy reachable Venti blocks from one server to another.

Command behavior:
- Usage: source host, destination host, and starting score, with options for fast destination check, ignore errors, visited memoization, rewrite broken pointers, explicit type, and verbosity.
- Determines the starting block type by probing unless `-t` is supplied.

Core behavior:
- `walk` skips zero scores, optionally skips already visited scores, optionally skips blocks already on destination, reads from source, recursively walks child references by type, writes to destination, and verifies score stability unless rewriting.
- Handles `VtRootType` by walking previous root and root score.
- Handles `VtDirType` by unpacking active `VtEntry` records and walking their scores.
- Handles pointer blocks by walking VtScore-sized score arrays with `type-1`.
- `ScoreTree` AVL memoization avoids revisiting score/type pairs.

Integration points:
- Uses Venti client APIs, `vtrootunpack`, `vtentryunpack`, `vtwrite`, `vtsync`, SHA1, AVL, and bin allocator.

Risks:
- In rewrite mode, unreadable child scores are replaced with zero scores, mutating copied metadata.
- Without `-m`, cycles or repeated shared blocks are handled only by content tree shape and zero checks, not memoization.
- Fast mode trusts destination `vtread` success as proof a block can be skipped.
