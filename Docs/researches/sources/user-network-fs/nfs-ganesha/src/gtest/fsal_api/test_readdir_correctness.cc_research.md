# sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_readdir_correctness.cc

## Purpose
This test validates FSAL `readdir` correctness for a large directory. It creates a directory named `test_directory` under the per-test root, populates it with `DIR_COUNT` entries, records each created object's key and expected generated name, and confirms that two directory scans return every handle exactly once.

## Important APIs, Types, And Functions
`ReaddirEmptyCorrectnessTest` creates/removes the test directory. `ReaddirFullCorrectnessTest` calls `create_and_prime_many`, records object keys with `obj_ops->handle_to_key`, duplicates them with `keyDup`, and later frees the duplicated key buffers. `rd_state_t` carries the recorded keys, boolean found flags, and names into `trc_populate_dirent`. `keyEQ` compares `gsh_buffdesc` keys by length and bytes.

## Control Flow, State, And Persistence
Setup creates 100,000 regular files under the test directory and stores stable handle keys before releasing each handle reference. It then calls `mdcache_lru_release_entries(-1)` to flush extra cached entries and force a stronger correctness check across cache boundaries. The `BIG` test calls `test_dir->obj_ops->readdir` twice with `whence = 0`, callback state, and `eod`, then asserts all entries were found after each pass and resets flags.

## Dependencies And Integration Points
The test integrates with the shared FSAL fixture, MDCACHE debug support, and object handle key generation. It uses Ganesha allocation (`gsh_malloc`, `gsh_free`) for duplicated key storage and the object callback contract that requires the callback to `put_ref` each provided object.

## Risks And Test Signals
The test is memory-heavy because it stores 100,000 key descriptors and names, and the callback performs a linear scan over all expected keys for each entry, creating O(n^2) behavior. It assumes generated names match `create_and_prime_many`'s `f-%08x` pattern. The disabled bypass test documents that direct sub-handle traversal is not currently compatible with object pointer comparisons. Strong signals are duplicate detection and full-entry coverage over two scans.
