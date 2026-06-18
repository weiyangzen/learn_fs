# sources/user-network-fs/pyfuse3/test/test_fs.py

Purpose: Integration tests for lower-level pyfuse3 features such as cache invalidation, notify-store, poll notification, timeout behavior, and termination.

Important APIs/types/functions: Fixtures `testfs` and `pollfs` mount `Fs` or `PollTestFs` in a forked process. Tests include `test_invalidate_entry`, `test_invalidate_inode`, `test_notify_store`, `test_notify_poll`, `test_entry_timeout`, `test_attr_timeout`, and `test_terminate`. Classes `Fs` and `PollTestFs` implement minimal `Operations` handlers. `run_fs` runs pyfuse3 in the child process.

Control flow: Parent process mounts a child-process filesystem and communicates state through a multiprocessing manager namespace. Tests trigger special behavior by setting xattr `command` on the mount or file. The filesystem then calls pyfuse3 APIs such as `invalidate_entry_async`, `invalidate_inode`, `notify_store`, `terminate`, and `PollHandle.notify`.

State and persistence: Test state is in manager namespace flags (`lookup_called`, `read_called`, timeouts, poll flags), child-process operation object fields, and kernel cache state. Filesystem content is a single virtual `message` file.

Dependencies and integration points: Depends on multiprocessing fork mode, Trio, pyfuse3, host FUSE, `select.poll`, and utility mount helpers.

Risks: Uses sleeps to wait for cache invalidation semantics and poll readiness, so timing can be flaky on slow systems. Fork-based tests reject multi-threaded parent processes. Poll tests rely on platform poll support.

Test signals: Strong signal for pyfuse3 invalidation/notification APIs and operation dispatch correctness beyond basic file IO.
