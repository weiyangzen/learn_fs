# sources/test-tools/xfstests-bld/fstests-bld/android-compat/getgrent.c

Purpose: provides simple group database iteration for Android builds that lack full `getgrent`, `setgrent`, and `endgrent` behavior.

Important APIs and functions: static `entries[]` contains `root` gid 0 and `fsgqa` gid 31415; exports `getgrent()`, `setgrent()`, and `endgrent()`. Debug-only helpers implement lookup tests.

Control flow: `getgrent` initializes `current_grp` to the first entry, returns entries until a null sentinel, then returns `NULL`. Reset functions clear `current_grp`.

State and persistence: static pointer `current_grp` is process-global iteration state. No external files such as `/etc/group` are read.

Dependencies and integration: compiled into `libandroid_compat` and used by tools expecting POSIX group iteration in the appliance environment.

Risks: not thread-safe, not reentrant, and only models two groups. `gr_mem` is `NULL`, which may surprise callers expecting a null-terminated member list pointer.

Test signals: debug-only main can check `root`, `fsgqa`, and missing lookups when compiled with `DEBUG`.
