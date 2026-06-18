# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl09.c

Purpose: legacy smoke test for nonblocking POSIX record locks with `F_SETLK`, covering both write and read lock placement followed by unlock.

Important APIs/types/functions: `fcntl(F_SETLK)`, `struct flock`, `F_WRLCK`, `F_RDLCK`, `F_UNLCK`, legacy `test.h`, `TEST`, `TEST_RETURN`, and temp file setup with `creat`/`open`.

Control flow: setup creates and opens a temp file and initializes flock whence/start/len/pid. Each loop sets `l_type` to write then read lock, calls `F_SETLK`, reports pass/fail, then sets `F_UNLCK` and unlocks before the next type.

State/persistence behavior: places and removes byte-range locks on one file. Lock region is whole file from current position because `l_len = 0`.

Dependencies/integration: legacy LTP harness and tempdir. No child process validates conflicts.

Risks/test signals: basic liveness only. It detects inability to set/unset locks but not cross-process semantics.
