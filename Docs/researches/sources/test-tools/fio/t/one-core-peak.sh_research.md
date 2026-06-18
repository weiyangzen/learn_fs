# sources/test-tools/fio/t/one-core-peak.sh

Purpose: root-only performance helper that tunes the host and block devices, chooses CPUs on the first physical core, and runs `t/io_uring` to estimate one-core block I/O peak throughput, optionally with latency reporting.

Important APIs and functions: shell functions handle argument parsing (`check_args()`), root/binary validation, CPU selection (`detect_first_core()`), sysfs device tuning (`check_io_scheduler()`, `check_sysblock_value()`), CPU governor tuning, NVMe/device reporting, kernel config reporting, and final command construction. `block_dev_name()` and `get_sys_block_dir()` normalize `/dev/*` paths into sysfs paths.

Control flow: after parsing `-h` and `-l`, the script requires root, validates tools, detects the local CPU/core for a single NVMe drive or falls back to CPU 0 for multiple drives, prints system and device metadata, forces scheduler and queue settings, checks NVMe poll queues, sets CPU scaling and idle governors, computes thread count from device count and sibling CPUs, then executes `taskset -c ... t/io_uring ...`.

State and persistence: it writes to `/sys/block/*/queue/*`, CPU frequency governor state, and CPU idle governor state. It does not restore prior settings. Output is printed to stdout/stderr only.

Dependencies and integration points: requires bash, root, `t/io_uring`, `lscpu`, `taskset`, `cpupower`, `dmidecode`, common coreutils, and optionally `nvme`, `journalctl`, `getenforce`, kernel config files, and NVMe sysfs topology. It is a manual tuning and benchmark helper rather than a fiotestlib unit.

Risks and test signals: risks include persistent host tuning changes, shell word-splitting around unquoted paths, assumptions about NVMe sysfs `address` and PCI locality, and failure on systems without cpupower or SELinux tools. The main signal is successful command execution and printed system/device context; warnings identify non-fatal missing optimizations such as disabled NVMe poll queues.
