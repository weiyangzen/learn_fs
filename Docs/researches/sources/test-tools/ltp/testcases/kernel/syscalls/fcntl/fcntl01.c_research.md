# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl01.c

Purpose: legacy broad smoke test for `fcntl(2)` commands `F_DUPFD`, `F_SETFL`, `F_GETFL`, `F_GETFD`, and `F_SETFD`.

Important APIs/types/functions: legacy LTP `test.h`, `tst_parse_opts`, `TEST_LOOPING`, `tst_tmpdir`, `fcntl`, `open`, `close`, `unlink`, `F_DUPFD`, `F_SETFL`, `O_NDELAY`, `O_APPEND`, `F_GETFD`, and `F_SETFD`.

Control flow: each loop creates eight temp files, closes selected fds to create holes, duplicates `fd[1]` with minimum fd values, validates returned fd positions, tests setting and clearing file status flags, then sets close-on-exec fd flag and checks `F_GETFD`.

State/persistence behavior: creates per-pid temp files, mutates descriptor table holes and duplicated descriptors, mutates file status flags on a shared open file description, and deletes files at loop end.

Dependencies/integration: uses old LTP harness and tempdir support rather than `tst_test.h`.

Risks/test signals: several checks only test bit presence, not exact flag values. Failures are unexpected duplicate fd numbers, flag mutation failures, or cleanup errors.
