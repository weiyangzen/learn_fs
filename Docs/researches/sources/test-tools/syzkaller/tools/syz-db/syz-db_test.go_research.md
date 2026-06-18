# sources/test-tools/syzkaller/tools/syz-db/syz-db_test.go

Purpose: this test validates `syz-db rm` behavior for a corpus record where a removed syscall produces a resource used by later calls.

Important APIs and flow: `TestDBRemoveMatchLine` creates a temporary corpus DB, saves a three-call Linux program containing `open$dir`, an ioctl that consumes `r0`, and `close(r0)`, then obtains the Linux/AMD64 target and calls `rm(fn, "open$dir", target)`. It reopens the DB and asserts the record contains only the ioctl and close calls with `0xffffffffffffffff` substituted for the removed fd resource.

State and persistence: the test owns a temporary DB path and deletes it with `defer os.Remove`. It depends on `db.Open`, `Save`, `Flush`, and reopening to observe on-disk state.

Dependencies and integration: uses `pkg/db`, `pkg/osutil.TempFile`, `prog.GetTarget`, Linux AMD64 target constants, and `testify/assert`.

Risks: the test covers one resource-rewrite case and one match string. It does not cover deleting all calls, multiple records, sequence preservation, broad substring matches, or deserialization failures.

Test signals: it is the primary regression signal for the `rm` command's backward removal and serialization semantics.
