# File Research: sources/virtualization/spdk/lib/ut_mock/mock.c

This file defines generic linker-wrapper hooks for SPDK unit tests.

`DEFINE_WRAPPER` creates wrappers for `calloc`, `pthread_mutex_init`, `pthread_mutexattr_init`, `recvmsg`, `sendmsg`, and `writev`, allowing tests to override or observe those calls through the mock framework.

It also defines a custom `__wrap_unlink()`. The wrapper succeeds only when `g_unlink_path` is set and matches the requested path; otherwise it returns `ENOENT`. If `g_unlink_callback` is set, it is invoked before success.

The notable behavior is that `__wrap_unlink()` returns positive `ENOENT`, not `-1` with `errno` set, so tests using it need to match this mock convention rather than POSIX unlink behavior.
