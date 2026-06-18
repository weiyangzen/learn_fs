# sources/security-integrity/selinux/restorecond/utmpwatcher.h
# sources/security-integrity/selinux/restorecond/utmpwatcher.h

Purpose: declares utmp watcher functions used by restorecond.

Important APIs and types: `utmpwatcher_handle(int inotify_fd, int wd)`, `utmpwatcher_add(int inotify_fd, const char *path)`, and `utmpwatcher_free()`.

State and persistence: implementation owns global in-memory user list and watch descriptor.

Dependencies and integration points: included by `restorecond.c` and `watch.c`.

Risks and test signals: no explicit error-reporting contract beyond return values from `handle`; fatal errors happen inside implementation. No direct tests.
