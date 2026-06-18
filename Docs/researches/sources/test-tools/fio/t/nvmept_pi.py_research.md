# sources/test-tools/fio/t/nvmept_pi.py

Purpose: destructive end-to-end protection information coverage for fio NVMe passthrough. It formats a target namespace through supported LBA formats, protection types, protection information locations, and metadata modes, then runs read/write and error tests for DIF/DIX options.

Important APIs and types: `DifDixTest` extends `FioJobCmdTest` and emits fio options such as `md_per_io_size`, `pi_act`, `pi_chk`, `apptag`, and `apptag_mask`. Device discovery helpers include `get_lbafs()`, `get_guard_pi()`, and `get_capabilities()`. `format_device()` wraps `nvme format`, and `difdix_test()` rewrites each test case for the current LBA format, PI type, and extended-LBA mode.

Control flow: `main()` parses fio path, target device, optional LBA formats, and ioengine. It discovers metadata-capable LBA formats, guard PI width, and namespace PI capabilities, injects filename/ioengine into `TEST_LIST`, then iterates over the cartesian product of `lbaf`, `pil`, `pitype`, and `elba`. For each combination it formats the device, creates a per-configuration artifact directory, adjusts block-size ranges and metadata buffer sizes, drops `REFTAG` checks for Type 3 PI, marks incompatible tests skipped, and invokes `run_fio_tests()`.

State and persistence: the namespace is reformatted multiple times with `sudo nvme format --force`, destroying data and changing metadata layout. Test dictionaries are mutated in place for each configuration. JSON outputs and logs persist under the selected artifact root. No rollback to the original format is attempted.

Dependencies and integration points: requires Python, fio, fiotestlib, nvme-cli, sudo, and a namespace with metadata and end-to-end data protection capability. It can use `io_uring_cmd` or `xnvme`; the xNVMe path adds `--thread=1` and `--xnvme_async=io_uring_cmd`. It plugs into the broader fio test system as a standalone executable harness.

Risks and test signals: risks include destructive formatting, stale mutable test options between product iterations, and device-specific behavior when `nvme nvm-id-ns` is unavailable, where the script assumes 16-bit guard PI. Positive tests require fio success and valid PI read/write behavior; negative tests intentionally use mismatched application tags, bad block sizes, or too-small metadata buffers and expect non-zero exits. Runtime and skipped counts are accumulated across all device configurations.
