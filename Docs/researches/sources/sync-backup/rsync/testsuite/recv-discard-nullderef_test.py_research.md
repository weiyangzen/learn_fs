## sources/sync-backup/rsync/testsuite/recv-discard-nullderef_test.py

Purpose: regression test for a receiver NULL dereference on the delta discard path when output temp creation fails.

Important APIs and control flow: skips as root or when chmod cannot deny writes. It creates a daemon module with destination basis dir `d`, a source file sharing a leading block with the basis, starts a daemon, chmods the destination dir to `0555`, and probes that `mkstemp` fails there. It then runs a client-to-daemon delta transfer with `--no-whole-file -a` to overwrite `d/f`. The expected result is exit 23, not exit 12 protocol error from receiver crash and not 0.

State and dependencies: daemon config, fixed port 12895, chmod restoration in `finally`, temporary-file writability probe, `RSYNC` command splitting.

Integration points: covers `receive_data()` discard path, delta token draining, and daemon receiver failure handling.

Risks and test signals: privilege/capability variance can skip. Exit-code distinction is precise: 12 indicates pre-fix crash, 23 indicates benign forced discard.
