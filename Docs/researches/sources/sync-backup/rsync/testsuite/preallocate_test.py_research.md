## sources/sync-backup/rsync/testsuite/preallocate_test.py

Purpose: validates receiver file allocation paths: `--preallocate`, `--preallocate --sparse`, and `--inplace --sparse` hole punching.

Important APIs and control flow: probes `--preallocate` support with a trivial transfer. `fs_can_punch_holes()` uses `ctypes` to call libc `fallocate(PUNCH_HOLE|KEEP_SIZE)` and observes block reduction. `seed_plain()` and `seed_holey()` create deep regular and zero-run files. The test verifies content after preallocation, asserts sparse allocation when punch holes are supported, then modifies a synced file to introduce a zero run and verifies `--inplace --sparse --no-whole-file` punches it.

State and dependencies: Linux/Cygwin allocation support, `st_blocks`, libc, random file contents, and deep scratch paths.

Integration points: covers syscall wrappers `do_fallocate` and `do_punch_hole`, sparse writer behavior, and inplace sparse updates.

Risks and test signals: filesystem capability varies; allocation assertions run only when the real punch-hole probe succeeds. Content equality is always required.
