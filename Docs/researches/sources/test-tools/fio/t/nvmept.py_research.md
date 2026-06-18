# sources/test-tools/fio/t/nvmept.py

## Purpose
Regression harness for fio's `io_uring_cmd` NVMe passthrough engine against an NVMe generic character device. It checks read/write/trim direction accounting, verification, queue-depth attainment, SQPOLL/fixed resource combinations, and flush command accounting.

## Important APIs, Types, and Functions
`PassThruTest` builds standard passthrough fio jobs with `--ioengine=io_uring_cmd --cmd_type=nvme` and validates nonzero/zero data-direction sections using `check_all_ddirs()`. It also requires the requested iodepth level 8 to be reached at least 95 percent. `FlushTest` builds jobs with `fsync` and checks `sync.total_ios` against expected write/fsync cadence. `TEST_LIST` defines 19 cases.

## Control Flow
`main()` parses required `--dut`, creates an artifact root, resolves fio, assigns the target device to every test, and runs the test list. Early tests cover sequential/random read, write, trim, mixed read/write, and trimwrite. Later tests enable fixed buffers/files, force async, SQPOLL, and validate flush behavior for read, write, readwrite, and trimwrite modes.

## State and Persistence Behavior
The script writes artifacts under `nvmept-test-<timestamp>`. It performs I/O directly to the provided NVMe character device and write/trim cases are destructive to device contents.

## Dependencies and Integration Points
Requires a fio build with `io_uring_cmd` NVMe support, Linux NVMe generic character devices such as `/dev/ng0n1`, JSON output, and the common Python runner. It exercises fio's NVMe command construction and accounting paths.

## Risks
The target device is destructive for write and trim tests. Tests assume the device can sustain iodepth 8; slow or constrained devices can fail the depth threshold despite functional correctness. Flush expectations allow one missing sync at tail but still assume stable `fsync` accounting. There is no requirement probe for device existence beyond fio failure.

## Test Signals
Passing cases prove direction-specific stats for read/write/trim/mixed passthrough commands, verify read-back on write tests, SQPOLL/fixed-resource compatibility for read/write/trim, and expected sync command counts for flush-enabled jobs.
