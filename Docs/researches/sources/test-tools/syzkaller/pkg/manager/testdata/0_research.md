# sources/test-tools/syzkaller/pkg/manager/testdata/0

Purpose: Crash-report fixture used by `TestGetSubsystems` in `crash_test.go`. It represents a Linux hung task / lock contention report whose stack includes block-layer paths.

Important content: The report begins with a blocked `syz.*` task, shows `bdev_open`, `blkdev_open`, `block/bdev.c`, and `block/fops.c`, then includes extensive lock and NMI backtrace data plus the report separator marker.

Control flow and state: The fixture is read as bytes, saved as a crash report through `CrashStore.SaveCrash`, then fed into `getSubsystems`. The expected subsystem result is `block`.

Dependencies and integration: Exercises the Linux reporter’s guilty-file extraction and subsystem extractor path rules. It also exercises report truncation/tail handling because the file contains a tail report separator.

Risks: Large kernel logs can include many unrelated subsystem paths; the test expects the extractor to choose the relevant block path rather than noise from lock listings or secondary NMI traces.

Test signals: Validates that a realistic hung-task report maps to the block subsystem.
