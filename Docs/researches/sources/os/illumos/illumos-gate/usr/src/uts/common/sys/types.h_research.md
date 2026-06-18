# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/types.h

## Purpose
Foundational illumos system type header defining scalar aliases, ABI-sized types, synchronization public structures, file/process/device identifiers, time types, limits, and compatibility aliases.

## Main Interfaces
- Defines common aliases such as `longlong_t`, `u_longlong_t`, `t_scalar_t`, `t_uscalar_t`, `uchar_t`, `ushort_t`, `uint_t`, `ulong_t`, `caddr_t`, `daddr_t`, `cnt_t`, and `ptrdiff_t`.
- Defines memory/storage and filesystem types including `pfn_t`, `pgcnt_t`, `spgcnt_t`, `off_t`, `off64_t`, `ino_t`, `blkcnt_t`, `fsblkcnt_t`, `fsfilcnt_t`, and their 64-bit forms.
- Defines `boolean_t` plus boolean conversion helpers.
- Defines alignment/padding unions and integer aliases for 32/64-bit ABI cleanliness.
- Defines identifiers including `id_t`, `lgrp_id_t`, `major_t`, `minor_t`, `pri_t`, old UID/device/inode types, `key_t`, `mode_t`, `uid_t`, `gid_t`, `datalink_id_t`, `taskid_t`, `projid_t`, `poolid_t`, `zoneid_t`, and `ctid_t`.
- Defines public pthread-compatible structures for mutexes, condition variables, rwlocks, once objects, attributes, and spinlocks.
- Defines `dev_t`, `nlink_t`, `pid_t`, `size_t`, `ssize_t`, `time_t`, `clock_t`, `clockid_t`, and `timer_t`.
- Defines limits such as `CHAR_BIT`, integer min/max values, `OFF_MIN`, `OFF_MAX`, and sentinel values `P_MYPID`, `P_MYID`, `NOPID`, `NODEV`, `NODEV32`, `PFN_INVALID`, and `PFN_SUSPENDED`.
- Includes `sys/select.h` at the end for legacy exposure requirements.

## Dependencies And Relationships
Includes `sys/feature_tests.h`, `sys/isa_defs.h`, `sys/machtypes.h`, integer type headers, and `sys/types32.h`. Almost every kernel and user-facing system header depends directly or indirectly on this file.

## Research Notes
This file is standards- and ABI-conditional throughout. Many typedefs vary by `_LP64`, large-file settings, XPG/POSIX feature macros, and kernel visibility, so changes here have broad compatibility impact.
