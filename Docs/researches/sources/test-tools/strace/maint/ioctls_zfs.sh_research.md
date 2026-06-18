# sources/test-tools/strace/maint/ioctls_zfs.sh

Purpose: scrapes OpenZFS ioctl definitions into strace ioctl table format.

Important APIs/types/functions: reads OpenZFS `META` version, constructs temporary C source/executable, helper `obtain`, includes `include/sys/fs/zfs.h` and `lib/libspl/include/sys/kstat.h`, compiles with `cc`, and executes generated code to print encoded constants.

Control flow: change to supplied OpenZFS clone, create temp source/executable, generate a C program that prints ioctl entries for selected ZFS/KSTAT constants, compile it with OpenZFS include paths, print a generated header plus hard-coded `BLKZNAME`, then run the executable.

State and persistence behavior: temporary files are removed by traps. No repository writes; stdout is intended to be captured into a generated header.

Dependencies and integration points: maintainer-only helper for updating `ioctls_zfs.h`, separate from Linux UAPI extraction because OpenZFS maintains its ABI outside Linux headers.

Risks: executes compiled code from the target OpenZFS headers, so it should be run only on trusted source trees. Assumes include layout and `META` version format.

Test signals: output should include the OpenZFS version and expected `ZFS_IOC_*`/`KSTAT_IOC_*` entries; compilation failure indicates include/API drift.
