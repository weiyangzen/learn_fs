# sources/test-tools/xfstests-bld/fstests-bld/android-compat/hasmntopt.c

Purpose: implements `hasmntopt` for Android, allowing callers to query comma-separated mount option strings in `struct mntent`.

Important APIs and functions: exported `hasmntopt(const struct mntent *mnt, const char *opt)` and debug-only test table/main.

Control flow: scans `mnt->mnt_opts` with `strstr`, checks option boundaries at start/comma and end/comma/equal, and returns a pointer to the match or `0`.

State and persistence: no mutable persistent state; reads the caller-provided mount option string.

Dependencies and integration: declared in `android_compat.h` and compiled into `libandroid_compat`.

Risks: uses substring search and advances by `len + 1`, so unusual overlapping option names may need careful review. Returns a mutable `char *` into the original option string.

Test signals: debug main checks positive matches for `foo`, `bar`, `baz` and negatives for absent names.
