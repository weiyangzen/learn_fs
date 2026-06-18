# sources/sync-backup/rsync/getgroups.c

## Purpose

`getgroups.c` is a portable helper that prints the current user's supplementary group ids, similar to `id -G`, while ensuring the user's primary gid appears in the output even on systems where `getgroups()` omits it.

## Important APIs, Types, And Functions

The only function is `main()`. It uses `MY_GID()` from rsync portability code, optionally calls `getgroups(0, NULL)` when `HAVE_GETGROUPS` is available, allocates a `gid_t` array of `n + 1`, fills it with `getgroups(n, list)`, prints each gid as an unsigned long with trailing spaces, tracks whether the primary gid was present, then prints the primary gid if missing.

## Control Flow

The program obtains the supplementary group count, allocates storage, fetches the group list, emits all returned gids, conditionally emits the primary gid, prints a newline, and exits 0. If `getgroups(0, NULL)` fails it reports through `perror()` and returns 1. If allocation fails it writes `out of memory!` and exits 1.

## State, Dependencies, And Integration

There is no persistent state. It depends on `rsync.h` for `gid_t`, `MY_GID()`, `UNUSED`, feature detection, and standard functions. It is a build/test utility for group-id portability and may be used by tests that need predictable group membership output.

## Risks

If the second `getgroups()` call fails, the code does not recheck `n` before iterating. Group membership can change between the count and fill calls. Output formatting has spaces between supplementary ids and may omit a separating space before the primary gid when no supplementary groups were printed, which is fine for whitespace-token parsing.

## Test Signals

Test with users whose primary gid is included and omitted from `getgroups()`, with zero supplementary groups, and on platforms without `HAVE_GETGROUPS`. Failure-path tests should simulate `getgroups()` and `malloc()` errors if possible.
