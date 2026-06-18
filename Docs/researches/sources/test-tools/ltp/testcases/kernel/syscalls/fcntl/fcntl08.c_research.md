# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl08.c

Purpose: basic `F_SETFL` test using `O_NDELAY | O_APPEND | O_NONBLOCK`.

Important APIs/types/functions: `fcntl(fd, F_SETFL, flags)`, `SAFE_OPEN`, `SAFE_CLOSE`, `TST_EXP_PASS`, and `lapi/fcntl.h`.

Control flow: setup opens a temp file. The single test calls `fcntl` to set the combined status flags and expects success.

State/persistence behavior: mutates file status flags on one open file description. It does not read back the flags.

Dependencies/integration: modern LTP tempdir test with GNU fcntl constants via LAPI.

Risks/test signals: narrow success-only check. It detects rejection of the flag set but not silent partial flag changes.
