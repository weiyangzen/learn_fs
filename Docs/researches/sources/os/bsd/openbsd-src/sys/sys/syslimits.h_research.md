# File Research: sources/os/bsd/openbsd-src/sys/sys/syslimits.h

Systemwide POSIX/BSD limit constants.

This header defines limits such as `ARG_MAX`, `CHILD_MAX`, `LINK_MAX`, `NAME_MAX`, `OPEN_MAX`, `PATH_MAX`, `PIPE_BUF`, `SYMLINK_MAX`, `SYMLOOP_MAX`, terminal/input limits, regex/utility limits, `IOV_MAX`, `TTY_NAME_MAX`, `LOGIN_NAME_MAX`, `HOST_NAME_MAX`, `GETENTROPY_MAX`, and `_MAXCOMLEN`.

Visibility macros gate POSIX, XPG, and BSD constants. Several values are directly ABI-significant for filesystem path parsing, link counts, descriptor defaults, symlink resolution, and pipe atomicity.

Filesystem/storage relevance: direct. `NAME_MAX`, `PATH_MAX`, `LINK_MAX`, `SYMLINK_MAX`, `SYMLOOP_MAX`, and `PIPE_BUF` are core VFS/userland contract limits.
