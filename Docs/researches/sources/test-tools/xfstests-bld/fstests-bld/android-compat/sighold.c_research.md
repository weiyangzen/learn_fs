# sources/test-tools/xfstests-bld/fstests-bld/android-compat/sighold.c

Purpose: implements legacy `sighold` and `sigrelse` APIs using POSIX signal masks for Android builds.

Important APIs and functions: static helper `set_to_int(sigset_t *set, int sig)`, exported `sighold(int sig)`, and `sigrelse(int sig)`.

Control flow: helper initializes a signal set with one signal. `sighold` blocks it via `sigprocmask(SIG_BLOCK)`, and `sigrelse` unblocks it with `SIG_UNBLOCK`.

State and persistence: changes the calling thread/process signal mask according to `sigprocmask` semantics.

Dependencies and integration: declared by `android_compat.h` and linked into compatibility library.

Risks: `sigprocmask` behavior in multithreaded programs can be subtle; callers expecting System V signal semantics should be reviewed.

Test signals: callers can verify the target signal is blocked/unblocked and return codes propagate from `sigprocmask`.
