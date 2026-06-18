# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/fix_grouping.h

Read completely: 36 lines.

This header declares `__fix_locale_grouping_str`.

Important interactions: included by locale loaders that need to normalize grouping strings.

Security/reliability notes: declaration-only header. The mutating behavior is only visible from the implementation, not encoded in the prototype.
