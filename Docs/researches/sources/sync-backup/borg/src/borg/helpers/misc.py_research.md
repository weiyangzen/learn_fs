# sources/sync-backup/borg/src/borg/helpers/misc.py

## Purpose
Miscellaneous runtime helpers for system diagnostics, multi-line logging, chunk iterator file wrappers, iterator consumption, tolerant broken-pipe text IO, and separated stream iteration.

## Important APIs, Types, And Functions
`sysinfo`, `log_multi`, `ChunkIteratorFileWrapper`, `open_item`, `chunkit`, `consume`, `ErrorIgnoringTextIOWrapper`, and `iter_separated`.

## Control Flow
`sysinfo` returns platform, Borg, Python, msgpack, FUSE, PID, CWD, argv, and SSH command information unless `BORG_SHOW_SYSINFO=no`. `ChunkIteratorFileWrapper.read` refills from a bytes iterator and assembles exactly up to requested bytes, invoking an optional progress callback on each read fragment. `open_item` wraps archive pipeline chunk fetching. `iter_separated` incrementally splits file reads by separator while preserving partial records across buffer boundaries.

## State And Persistence
`ChunkIteratorFileWrapper` stores the current memoryview, offset, exhaustion flag, iterator, and callback. `ErrorIgnoringTextIOWrapper` closes itself after broken pipes. `sysinfo` only reads environment/process state.

## Dependencies And Integration Points
Depends on Borg logger, msgpack wrapper, FUSE selection, archive pipeline `fetch_many`, and repository object type constants. It supports command diagnostics and streaming file contents from archives.

## Risks And Edge Cases
`sysinfo` imports FUSE selection and may reflect optional dependency availability. `ChunkIteratorFileWrapper.read` does not implement all file-like methods and can return memoryview slices joined as bytes. Broken-pipe wrapper intentionally hides write/read failures after closure. `iter_separated` does not trim separators and must handle both str and bytes streams consistently.

## Test Signals
Tests should cover sysinfo environment suppression, multi-line logging levels, chunk reads across boundaries, read callbacks, `chunkit` partial final chunks, `consume`, broken pipe suppression, and separator iteration with trailing separators.
