# sources/storage-engines/tikv/tests/failpoints/cases/test_backup.rs

Purpose: tests backup behavior when an async prewrite holds a memory lock.

Important APIs and functions: `backup_blocked_by_memory_lock` uses `TestSuite`, `kv_prewrite`, `suite.backup`, and checks `brpb::Error_oneof_detail::KvError`.

Control flow: pauses `raftkv_async_write_finish`, starts a prewrite with async commit in another thread, sleeps to let the in-memory lock exist, runs backup over `a..z` at backup ts 21, and expects a locked key error. It then removes the failpoint, joins the thread, and stops the suite.

State and persistence: the important state is an in-memory lock not yet fully written through the async write path. Backup observes this lock and refuses to silently skip it.

Dependencies and integration: uses backup test harness, futures stream collection, temp storage path, and KV RPC protobufs.

Risks and test signals: uses fixed sleep to wait for the lock. Signal is correctness of backup conflict detection against transient memory locks.
