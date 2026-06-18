# Research: sources/storage-engines/wiredtiger/test/checkpoint/recovery-test.sh

## sources/storage-engines/wiredtiger/test/checkpoint/recovery-test.sh

Purpose: Shell harness that repeatedly snapshots a running checkpoint test home and verifies copied homes recover cleanly.

Important flow: accepts config, home directory, and optional binary name (default `t`). It starts the binary with config and `-h home`, redirects output to `$home.out`, traps exit/signals to kill the child, waits until the output contains "Finished a checkpoint", then repeatedly `SIGSTOP`s the process, copies the home to backup, resumes the process, copies backup to recovery, and runs the binary in verify-only mode (`-t r -D -v -h recovery`). If the original config included `-e`, recovery also passes `-e -x`.

State and persistence: creates/removes `$home.backup`, `$home.recovery`, `$home.out`, and copies database files while the process is stopped. Final cleanup removes home and output.

Dependencies/integration: depends on POSIX signals, `grep`, `cp`, shell process control, and the checkpoint test's verify-only path. Risks include unsafe unquoted `$config`, copy races if STOP has not fully quiesced all threads, and platform limitations. Test signals are recovery binary exit status and loop completion when the child exits.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/checkpoint/recovery-test.sh -->
