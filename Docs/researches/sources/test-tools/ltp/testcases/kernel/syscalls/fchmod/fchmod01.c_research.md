# sources/test-tools/ltp/testcases/kernel/syscalls/fchmod/fchmod01.c

Purpose: positive coverage for changing regular-file mode through `fchmod(2)` across several permission and special-bit combinations.

Important APIs/types/functions: `fchmod`, `SAFE_OPEN`, `SAFE_FSTAT`, `SAFE_CLOSE`, `TEST`, `TST_RET`, `tst_res`, and constants from `fchmod.h`.

Control flow: setup creates `testfile`. `verify_fchmod()` iterates over modes `0`, execute-only groups, `0777`, and setuid/setgid/sticky combinations, calls `fchmod(fd, mode)`, stats the fd, and compares mode bits after removing `S_IFREG`.

State/persistence behavior: one open file's mode is repeatedly mutated. Each iteration overwrites the previous mode; no content is written.

Dependencies/integration: modern LTP tempdir test. It assumes the filesystem preserves the tested permission and special bits according to normal Linux rules for the current user.

Risks/test signals: failure can come from syscall failure or mode mismatch. The test's comparison masks only the regular-file type bit, so unexpected extra mode bits are visible.
