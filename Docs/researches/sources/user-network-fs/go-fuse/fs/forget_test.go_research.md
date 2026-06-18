# sources/user-network-fs/go-fuse/fs/forget_test.go

Purpose: validates inode FORGET cleanup, memory compaction expectations, and `NodeOnForgetter` callbacks.

Important tests/types: `allChildrenNode` dynamically produces a 100x100 tree; root-only Linux `TestForget` walks it, drops kernel dentries via `/proc/sys/vm/drop_caches`, waits for TTL, and expects only root in `kernelNodeIds`. `forgetTestRootNode`/`forgetTestSubNode` count `OnForget`; `TestOnForget` verifies rmdir alone does not forget persistent child, `ForgetPersistent` triggers child/dir callbacks, and unmount triggers root callback.

Dependencies/state: root/Linux required for cache drop; uses lookup counts, persistent inodes, and bridge maps.

Risks/test signals: strong lifecycle coverage but environment-sensitive. Timing around FORGET processing is acknowledged with sleeps.
