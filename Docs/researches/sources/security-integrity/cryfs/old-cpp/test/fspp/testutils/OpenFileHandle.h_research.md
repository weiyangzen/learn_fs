# sources/security-integrity/cryfs/old-cpp/test/fspp/testutils/OpenFileHandle.h

Purpose: defines a non-copyable RAII wrapper around a POSIX-style file descriptor for tests.

Important APIs/types: constructors call `::open(path, flags)` or `::open(path, flags, mode)`, preserving `errno` into `errno_` when open fails. `fd()` returns the descriptor, `errorcode()` returns captured errno, and `release()` prevents destructor close.

Control flow: destructor closes any non-negative descriptor. On Apple it sleeps 50 ms after close to allow file-release timing in macOS tests.

State/persistence: state is the descriptor integer and immutable saved errno. It affects real filesystem state only through open/close.

Dependencies/integration: includes `fcntl.h`, `errno.h`, platform `unistd.h` or `io.h`, thread/chrono, and cpp-utils copy prevention.

Risks: `fd()` and `errorcode()` are non-const. `release()` leaks ownership intentionally, so tests must close externally. No retry on interrupted close.

Test signals: supports tests needing deterministic fd cleanup and access to open failure errno.
