<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/midx.py -->
# sources/sync-backup/bup/lib/bup/midx.py

## Purpose
This module reads and validates bup multi-index (`.midx`) files, which aggregate multiple Git `.idx` files to accelerate object existence checks in repositories with many packs.

## Important APIs, Types, And Functions
Important items are `MIDX_HEADER`, `MIDX_VERSION`, `MissingIdxs`, `PackMidx`, `open_midx()`, and `clear_midxes()`. `PackMidx.exists()` supports source-index reporting but not pack offsets.

## Control Flow
`open_midx()` mmaps a candidate file, verifies header/version, handles too-old/too-new files with warnings, and constructs `PackMidx`. `PackMidx.__init__()` parses fanout bits, sha table, index selector table, and nul-separated idx names, then verifies each referenced idx exists. Lookup uses extracted leading bits to choose a fanout range and interpolated search over sorted SHA values.

## State And Persistence Behavior
The object owns an mmap and exposes iterable SHA entries. Persistent state is the `.midx` file and its referenced `.idx` files. `clear_midxes()` deletes all midx files in a directory.

## Dependencies And Integration Points
It depends on `_helpers.extract_bits`/`firstword`, mmap helpers, and logging. `git.PackIdxList` loads midx files, removes redundant or missing ones, and uses source hints from `PackMidx` when deduplicating writes.

## Risks And Edge Cases
Missing constituent idx files either raise `MissingIdxs` or cause `open_midx()` to return `None` depending on `ignore_missing`. Offset lookup is unsupported, so callers needing offsets must reopen the source idx. The interpolation formula assumes sorted hash distribution and well-formed fanout ranges. Close discipline matters because maps can keep files alive while auto-midx rewrites.

## Test Signals
`test/int/test_midx.py` and `test/int/test_git.py` cover missing idx behavior, check mode, midx close/refresh interactions, and object lookup through `PackIdxList`.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/midx.py -->
