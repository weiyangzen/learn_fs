# File Research: sources/os/bsd/dragonflybsd/sys/sys/signal.h

This header defines the public signal ABI: signal numbers, signal sets, signal actions, alternate stacks, event notification, and signal-related userland declarations.

Key responsibilities:
- Defines `pid_t`, `size_t`, and `uid_t` where needed.
- Defines sigset indexing macros:
  - `_SIG_MAXSIG`
  - `_SIG_IDX`
  - `_SIG_WORD`
  - `_SIG_BIT`
  - `_SIG_VALID`
- Defines standard and BSD signal numbers, including:
  - traditional signals 1-34
  - checkpoint signals `SIGCKPT` and `SIGCKPTEXIT`
  - realtime range `SIGRTMIN` to `SIGRTMAX`
- Defines handler type `__sighandler_t` and sentinel handlers:
  - `SIG_DFL`
  - `SIG_IGN`
  - `SIG_ERR`
- Defines `struct sigevent` and notification types:
  - `SIGEV_NONE`
  - `SIGEV_SIGNAL`
  - `SIGEV_THREAD`
  - BSD `SIGEV_KEVENT`
- Defines `sigset_t` and includes machine signal definitions after it is available.
- Defines POSIX `struct sigaction`, handler/sigaction aliases, and signal action flags.
- Defines BSD `NSIG`, `SI_UNDEFINED`, `sig_t`, and `struct sigvec`.
- Defines alternate signal stack flags and sizes:
  - `SS_ONSTACK`
  - `SS_DISABLE`
  - `MINSIGSTKSZ`
  - `SIGSTKSZ`
- Defines `SIG_BLOCK`, `SIG_UNBLOCK`, and `SIG_SETMASK`.
- Declares `signal()` and BSD `sigblockall()`/`sigunblockall()`.

Important invariants:
- `_SIG_MAXSIG` is 128, while BSD-visible `NSIG` is 64 for historical `sigptbl` sizing.
- `SIGKILL` and `SIGSTOP` are the uncatchable/unignorable signals in later kernel macros.
- `struct sigaction` stores handler and sigaction callback in a union; `SA_SIGINFO` determines which is meaningful.
- `SIG_EINTR` is described in comments as an internal no-delivery interrupt cause, but no public define appears in this header.

Research notes:
- This is a visibility-gated ABI header with POSIX, XSI, and BSD surfaces interleaved.
