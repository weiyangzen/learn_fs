<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/26 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/26

## Purpose
This older lockdep fixture covers the same loop-device circular dependency as report 250 on a 4.14-era kernel. The expected title is `possible deadlock in blkdev_reread_part` and type `LOCKDEP`.

## Important APIs, Types, and Functions
Headers include `TITLE` and `TYPE`. Parser paths include circular locking dependency detection and lockdep stack extraction. Key symbols include `blkdev_reread_part`, `lo_compat_ioctl`, `__lock_acquire`, `lo_release`, `__blkdev_put`, `loop_reread_partitions`, `loop_set_status`, `loop_set_status_compat`, `compat_blkdev_ioctl`, `compat_SyS_ioctl`, and `entry_SYSENTER_compat`.

## Control Flow
The reporter identifies `WARNING: possible circular locking dependency detected`, reads the lock chain and stack backtrace, and chooses `blkdev_reread_part` as the acquisition site responsible for the title.

## State and Persistence Behavior
The source is an immutable 82-line lockdep log. Expected state is the lockdep title/type; no panic or corruption flag is stored.

## Dependencies and Integration Points
It depends on Linux lockdep regexes and generic `ParseTest` comparison, and complements report 250 with a different kernel's output style.

## Risks and Edge Cases
Kernel-version differences in syscall labels and lockdep helper names should not change the normalized title. Parser frame scoring must not pick `lo_compat_ioctl`.

## Test Signals
Stable output is `possible deadlock in blkdev_reread_part` with `TYPE: LOCKDEP`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/26 -->
