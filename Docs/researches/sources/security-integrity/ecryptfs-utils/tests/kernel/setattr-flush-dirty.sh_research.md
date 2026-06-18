## sources/security-integrity/ecryptfs-utils/tests/kernel/setattr-flush-dirty.sh

Purpose: Shell-only regression test for dirty-page flushing during setattr, tied to kernel bug 33372. It verifies that preserving timestamps during copy remains stable after sync through an eCryptfs mount.

Important APIs and functions: `test_same_timestamp`, `stat -c '%y'`, `touch`, `sync`, `sleep`, `cp -p`, and normal `etl_*` setup/cleanup. Control flow creates `original`, syncs and waits, copies with preserved metadata to `copy`, compares timestamps, syncs again, compares timestamps again, removes both files, and exits.

State and persistence: Creates two transient files whose timestamps are the test state. Dependencies include eCryptfs setattr/writeback behavior, lower mount, and system timestamp precision. Integration is a kernel safe/destructive test depending on harness categorization. Risks include timestamp granularity or clock quirks; the one-second sleep reduces ambiguity, while the second comparison specifically targets dirty-page side effects after sync.
