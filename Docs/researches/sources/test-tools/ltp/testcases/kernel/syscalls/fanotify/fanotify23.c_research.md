# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify23.c

Purpose: tests evictable fanotify inode marks. It verifies upgrade from evictable to non-evictable, refusal to downgrade, ignored-mask behavior, eviction-driven mark removal, and restoration of events after cache eviction removes an evictable ignored mark.

Important APIs/types/functions: `fanotify_init`, `fanotify_mark`, `FAN_MARK_EVICTABLE`, `FAN_MARK_IGNORED_MASK`, `FAN_MARK_IGNORED_SURV_MODIFY`, `FAN_MARK_FILESYSTEM`, `FAN_ATTRIB`, `/proc/sys/vm/drop_caches`, `/proc/sys/vm/vfs_cache_pressure`, `fsync`, and `FAN_NONBLOCK`.

Control flow: setup creates the file, probes evictable mark and filesystem `FAN_ATTRIB` support, and raises vfs cache pressure. The test adds an evictable mark, upgrades it, expects `EEXIST` when trying to downgrade, verifies removal after empty mask, installs a filesystem `FAN_ATTRIB` watch, confirms chmod generates an event, adds an evictable ignored mask on the file, confirms chmod is ignored, drops caches twice, verifies mark removal with `ENOENT`, then confirms chmod events return.

State/persistence behavior: mutates file modes, kernel mark state, inode cache state, and global vfs cache pressure, which LTP save/restore handles. A mount cycle flushes pending mark destruction.

Dependencies/integration: restricted to ext2 because shrinker behavior is predictable enough for eviction. Requires root, mounted scratch device, and writable VM sysctls.

Risks/test signals: cache eviction is inherently environment-sensitive. Passing requires expected `EEXIST`, expected no event while ignored, expected `ENOENT` after eviction, and exactly the expected `FAN_ATTRIB` events.
