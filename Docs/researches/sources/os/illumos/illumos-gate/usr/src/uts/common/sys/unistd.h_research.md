# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/unistd.h

## Purpose
Implementation-specific constants behind public `unistd.h`, especially `confstr`, `sysconf`, `pathconf`, and standards feature values.

## Main Interfaces
- Defines `confstr` names such as `_CS_PATH`, large-file build options, XBS5, and POSIX V6 compilation environments.
- Defines many `sysconf` names for POSIX, SVR4, XPG, realtime, threads, hardware cache/CPU properties, UNIX 98/03/08 features, IPv6, and raw sockets.
- Defines `pathconf` names for path/name limits, async/prioritized/synchronized I/O, allocation transfer sizes, symlink behavior, ACLs, case behavior, system attributes, timestamp resolution, file size bits, and extended attributes.
- Defines related values such as `_PC_LAST`, `_CASE_SENSITIVE`, `_CASE_INSENSITIVE`, `_ACL_ACLENT_ENABLED`, and `_ACL_ACE_ENABLED`.
- Defines standards version and support macros including `_POSIX_VERSION`, `_POSIX2_VERSION`, `_XOPEN_XPG3`, `_XOPEN_XPG4`, `_XOPEN_UNIX`, `_XOPEN_REALTIME`, `_XOPEN_ENH_I18N`, `_XOPEN_SHM`, and POSIX2 capability flags.

## Dependencies And Relationships
Includes `sys/feature_tests.h`. This file explicitly warns applications to include public `<unistd.h>` instead; it is the implementation constant source used by libc and system headers.

## Research Notes
The numeric `_SC`, `_PC`, and `_CS` values are externally observable through `sysconf`, `pathconf`, and `confstr`, so additions must preserve existing values and update consumers like tracing tools when required.
