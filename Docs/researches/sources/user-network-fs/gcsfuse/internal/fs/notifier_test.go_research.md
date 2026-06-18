# sources/user-network-fs/gcsfuse/internal/fs/notifier_test.go

Purpose: tests that FUSE notifier invalidation prevents stale cached dentries from causing persistent failures after a GCS object is clobbered outside the mounted filesystem.

Important APIs/types: `NotifierTest` embeds `fsTest`. `SetupSuite` enables implicit directories, sets a long inode attribute cache TTL, installs `fuse.NewNotifier`, enables experimental dentry cache, enables streaming writes, and starts the filesystem. Tests use `storageutil.CreateObject` to create and then clobber bucket objects behind gcsfuse’s back.

Control flow and state: `TestWriteFileWithRootDirParent` creates `fileName` in GCS, stats it to cache the entry, overwrites the object in GCS to change generation, then writes through the mount. The first write should fail with `ESTALE`, and the second write should succeed after notifier invalidation. `TestWriteFileWithNonRootDirParent` repeats the same scenario for `dir/foo`, validating parent lookup/invalidation below root. `TestReadFileDoNotFailPersistently` performs a stale read after clobber and expects the second read to succeed once the entry has been invalidated.

Dependencies and integration: uses mounted filesystem helpers from `common`, fake bucket storage utilities, `fuse.NewNotifier`, cfg dentry-cache and streaming-write options, syscall error matching, and long cache TTLs to make stale entries observable.

Risks: assertions depend on stale generation detection and notifier support. The exact first read error is only checked as non-nil, while write tests check `ESTALE`. The tests do not verify notification counts or exact parent invalidation calls; they validate externally visible recovery.

Test signals: a failure means stale cached inode/dentry state can persist after clobbering, causing repeated user-visible failures rather than one stale-handle error followed by recovery.
