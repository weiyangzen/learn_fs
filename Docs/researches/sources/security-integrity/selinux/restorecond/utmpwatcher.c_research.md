# sources/security-integrity/selinux/restorecond/utmpwatcher.c
# sources/security-integrity/selinux/restorecond/utmpwatcher.c

Purpose: tracks logged-in users through `/run/utmp` so root restorecond can expand `~` patterns for active user homes.

Important APIs and control flow: `utmpwatcher_handle()` ignores unrelated watch descriptors, reads `/run/utmp`, builds a sorted list of `USER_PROCESS` usernames, re-adds an inotify watch on utmp, compares old/new lists with `strings_list_diff()`, and returns whether users changed. `utmpwatcher_add()` initializes utmp state if needed and calls `watch_file()` to add the configured suffix under each logged-in user's home. `utmpwatcher_free()` releases the user list.

State and persistence: keeps global `utmp_ptr` and `utmp_wd`; no durable state.

Dependencies and integration points: used by `watch.c` when config paths begin with `~` in root mode.

Risks and test signals: hard exits if `/run/utmp` cannot be read or watched. Usernames are mapped through `getpwnam()` and missing passwd entries are skipped. No direct tests.
