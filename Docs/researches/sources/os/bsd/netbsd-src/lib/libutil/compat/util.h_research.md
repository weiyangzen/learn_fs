# File Research: sources/os/bsd/netbsd-src/lib/libutil/compat/util.h

## Purpose
Compatibility declarations for old `libutil` APIs.

## Key Details
- Declares old ABI functions using `utmp50`, `utmpx50`, `passwd50`, and `int32_t` time.
- Declares current-version internal entry points with `__...50` names for wrappers to call.
- Covers login accounting, `parsedate`, and password database helpers.

## Dependencies and Role
- Main compatibility header used by the compat C wrappers in this batch.
