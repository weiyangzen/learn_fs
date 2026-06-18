# sources/sync-backup/bup/lib/bup/_helpers.c

## Purpose
Main native Python extension module for bup performance and platform primitives. It combines sparse writing, rolling checksums, Bloom/midx/idx operations, random data generation, no-atime opens, Linux attributes, passwd/group wrappers, readline integration, ACL support, vint packing, string parsing, and hashsplit type registration.

## Important APIs, Types, and Functions
Exports methods `write_sparsely`, `selftest`, `rollsum`, `bitmatch`, `firstword`, `bloom_contains`, `bloom_add`, `extract_bits`, `merge_into`, `write_idx`, `write_random`, `random_sha`, `open_noatime`, `openat_noatime`, optional `get_linux_file_attr`/`set_linux_file_attr`, passwd/group lookups, hostname, optional readline callbacks, optional `read_acl`/`apply_acl`, `vuint_encode`, `vint_encode`, `limited_vint_pack`, and `strtoimax`.

## Control Flow
Module init calls `hashsplit_init`, creates the module, validates integral assumptions, sets constants, detects stderr TTY, imports `math.inf`, and registers types. Individual functions are mostly direct C/POSIX operations with Python argument parsing and overflow checks.

## State and Persistence Behavior
State includes module state `istty2`, global readline callback pointers, infinity objects, and hashsplit type globals. Persistent effects include writing sparse regions to fds, writing idx/midx mmaps, changing Linux file flags, applying ACLs, and reading account databases.

## Dependencies and Integration Points
Depends on generated config feature macros, Python C API, POSIX I/O, mmap/msync, Linux fs ioctls, readline, libacl, `bupsplit`, `_hashsplit`, and bup integer/pyutil helpers. It is the backend for Python modules such as `bup.bloom`, `bup.git`, sparse restore code, shell readline support, and metadata ACL handling.

## Risks and Test Signals
Risks are memory/buffer misuse, overflow, platform feature mismatch, endian/pack-index format errors, sparse-hole miscalculation, readline callback lifetime leaks, ACL unavailable behavior, and dirty mmap flushing. Signals include extension import, rollsum selftest, Bloom membership tests, idx/midx validation by Git, sparse-size tests, no-atime fallback, ACL round trips, and vint encode/decode compatibility.
