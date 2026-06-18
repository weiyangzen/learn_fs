# File Research: sources/local-fs/xfsprogs/db/sig.c

Small SIGINT handling layer for `xfs_db`.

Key responsibilities:
- Installs a SIGINT handler in `init_sig`.
- Tracks interruption state in `gotintr`.
- Provides helpers to block/unblock SIGINT, clear the flag, and query whether SIGINT was seen.

Important behavior:
- Uses `sigaction` with `sa_sigaction` but does not set `SA_SIGINFO`.
- `blockint`/`unblockint` manipulate a process signal mask containing only SIGINT.

Dependencies:
- Uses libc signal APIs and `libxfs.h`.

Notable risks:
- `gotintr` is a plain `int`, not `volatile sig_atomic_t`; signal-handler correctness is minimal.
