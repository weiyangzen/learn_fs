# Research: sources/user-network-fs/rclone/fs/operations/reopen_test.go

## sources/user-network-fs/rclone/fs/operations/reopen_test.go

Purpose: unit tests for `ReOpen` retry, seek, range, unknown-size, `ReadAt`, close, and accounting behavior. It defines `reOpenTestObject`, a mock object wrapper whose `Open` asserts requested start offsets and injects read or open failures at configured byte breakpoints.

Control flow runs the same nested test set across normal, range-option, seek-option, and unknown-size modes. It checks full reads, EOF, rewind, double close, immediate open error, retry recovery, too-many-retries sticky errors, `ReadAt` position preservation, seek validation, seek-from-end restrictions for unknown size, and accounting delay/error propagation. State is test-only expected offsets, injected break slices, accounting totals, and mock object size flags. Dependencies include `mockobject`, `fs.RangeOption`, `fs.SeekOption`, `HashesOption`, `pool.DelayAccountinger`, and `readers.ErrorReader`. Risks covered are option mutation by `fs.FixRangeOption`, hash options during ranged reopens, retry counters reset on seek, and serialized ReaderAt semantics. Test signal is high for the reader state machine.
