<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/250 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/250

## Purpose
This lockdep fixture verifies circular-locking report parsing for the loop block-device path. The expected title is `possible deadlock in blkdev_reread_part` and type `LOCKDEP`.

## Important APIs, Types, and Functions
The source uses `TITLE` and `TYPE` headers. Parser paths include Linux lockdep circular-dependency matching, lock-chain report extraction, frame selection, and type mapping to `LOCKDEP`. Key symbols include `blkdev_reread_part`, `lo_compat_ioctl`, `lo_release`, `__blkdev_put`, `lo_open`, `__blkdev_get`, `loop_reread_partitions`, `loop_set_status`, `compat_blkdev_ioctl`, and `entry_SYSENTER_compat`.

## Control Flow
The reporter sees `WARNING: possible circular locking dependency detected`, reads the attempted lock `&bdev->bd_mutex`, the held lock `&lo->lo_ctl_mutex#2`, the reverse dependency chain, the unsafe locking scenario, and the stack backtrace. It must title the report from the acquisition site `blkdev_reread_part`, not from lockdep helper frames.

## State and Persistence Behavior
There is no runtime state. The fixture persists one complete lockdep report including lock classes, dependency chain, and 32-bit compat syscall context.

## Dependencies and Integration Points
It depends on syzkaller's lockdep oops patterns, stack-frame parsing, and `crash.Type` conversion. Integration is via `TestParse` on Linux report fixtures.

## Risks and Edge Cases
The report contains multiple historical stack traces for lock classes before the final backtrace. Parser changes can accidentally choose `lo_release` or `lo_open` instead of the current acquisition frame.

## Test Signals
The parse must return title `possible deadlock in blkdev_reread_part` with type `LOCKDEP` and no panic/corruption flags.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/250 -->
