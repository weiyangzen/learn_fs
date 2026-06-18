# sources/test-tools/xfstests-bld/fstests-bld/android-compat/android_compat.h

Purpose: compatibility header that declares or defines libc features missing from Android bionic for xfstests and related tools.

Important APIs and functions: defines `DEV_BSIZE`, `ino64_t`, permission aliases, and prototypes for `basename`, `hasmntopt`, `seekdir`, `telldir`, `sighold`, `sigrelse`, `getsubopt`, `valloc`, SysV shared memory functions, and `sync_file_range`.

Control flow: purely preprocessor declarations, guarded to avoid x86/x86_64 and repeated inclusion. It is meant to be force-included for target builds, not build-host tools.

State and persistence: no runtime state. It shapes compile-time ABI assumptions.

Dependencies and integration: used by `build-all` via `-include android_compat.h` for Android builds and installed by the android-compat Makefile.

Risks: declaring libc/kernel interfaces manually can drift from bionic or kernel headers. The architecture guard excludes x86/x86_64 Android builds.

Test signals: component builds compile without missing symbol/prototype errors when this header is included.
