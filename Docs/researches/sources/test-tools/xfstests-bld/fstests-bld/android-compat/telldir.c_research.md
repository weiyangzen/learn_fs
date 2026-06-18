# sources/test-tools/xfstests-bld/fstests-bld/android-compat/telldir.c

Purpose: implements `telldir` and `seekdir` for Android by relying on bionic's internal `DIR` layout.

Important APIs and functions: local redefinition `struct DIR { int fd_; }`, exported `long telldir(struct DIR *dirp)`, and `void seekdir(DIR *dirp, long loc)`.

Control flow: `telldir` returns `lseek(dirp->fd_, 0, SEEK_CUR)`. `seekdir` calls `lseek(dirp->fd_, loc, SEEK_SET)` and ignores the return.

State and persistence: manipulates directory stream kernel file offset. No local persistent state.

Dependencies and integration: depends on the first field of bionic `DIR` being the file descriptor, as documented in the source comment. Declared in `android_compat.h`.

Risks: intentionally relies on private libc layout, so it can break if bionic changes `DIR`. Error returns from `seekdir` are discarded.

Test signals: directory iteration code using `telldir`/`seekdir` works on the Android target without crashes or incorrect offsets.
