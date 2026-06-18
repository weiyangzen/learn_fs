# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl10.c

Purpose: legacy smoke test for blocking POSIX record locks with `F_SETLKW`, covering write/read lock placement and unlock on an uncontended file.

Important APIs/types/functions: `fcntl(F_SETLKW)`, `struct flock`, `F_WRLCK`, `F_RDLCK`, `F_UNLCK`, legacy LTP `TEST`, and temp file setup.

Control flow: setup creates a temp file and initializes flock fields. Each loop tries a write lock and unlock, then a read lock and unlock using `F_SETLKW`, reporting success for each call.

State/persistence behavior: places and removes whole-file locks on one fd. Since there is no competing process, `F_SETLKW` should not block.

Dependencies/integration: legacy LTP tempdir and signal pause handling.

Risks/test signals: only validates uncontended blocking command path. It will not detect incorrect wakeup/deadlock behavior.
