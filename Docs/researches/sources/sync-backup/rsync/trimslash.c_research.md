# sources/sync-backup/rsync/trimslash.c

Purpose: tiny test harness utility for `trim_trailing_slashes()`. It exists only to expose the shared path function as an executable for tests.

Important APIs and flow: defines stub globals required by `syscall.o`, checks at least one argument, then mutates each `argv[i]` in place with `trim_trailing_slashes()` and prints the result. Return code is `1` for missing args and `0` after processing.

State and persistence: no persistent state and no filesystem access. It writes normalized paths to stdout.

Dependencies and integration: includes `rsync.h` and links shared utility/syscall code. It is exercised by `trimslash_test.py`. Risks are minimal; because it edits argv memory directly, it assumes command-line argument storage is mutable on supported platforms, which is conventional for C programs but still a portability assumption. Test signal is exact stdout matching over edge-case slash inputs.
