# sources/sync-backup/bup/lib/bup/cmd/midx.py

## Purpose
`midx.py` builds, checks, and prunes multi-index files that aggregate many pack indexes into faster lookup structures.

## APIs and Control Flow
`_maybe_open_midx` handles missing referenced idx files and optionally removes broken midx files. `check_midx` verifies sub-index membership, midx membership, and ordering. `_do_midx` opens idx/midx inputs, calculates a fanout table size from object count/pages, writes an atomic `.midx` header/table/object/name map, and uses `_helpers.merge_into` over an mmap. `do_midx_dir` removes redundant midxes, groups inputs according to high/low water marks and fd limits, and repeatedly calls `do_midx_group`. `main(argv)` validates modes, resolves pack dir, fd limits, check/build/auto/force behavior, and optional printed names.

## State, Dependencies, Integration, Risks, Tests
Persistent state is `.midx` files in `objects/pack`; auto/force can remove redundant or broken midxes. Dependencies include `git.open_idx`, `midx.open_midx`, `resource.RLIMIT_NOFILE`, atomic file replacement, fsync, mmap, and object index layout. It integrates with lookup-heavy commands and GC, which clears midxes before rewriting packs. Risks include fd limit miscalculation, broken midx cleanup, output filename collisions, stale references, and correctness of sorted object merges. Test signals include check failures, missing idx handling, auto thresholds, force single-output behavior, max-files grouping, atomic output, and redundant midx deletion.
