# sources/test-tools/fio/t/io_uring_pi.py

## Purpose
Destructive NVMe protection-information regression harness for fio's `io_uring` engine. It formats a target namespace with supported LBA formats, protection types, and PI locations, then tests DIF/DIX metadata read/write behavior.

## Important APIs, Types, and Functions
`DifDixTest` extends `FioJobCmdTest` and builds fio jobs with `--ioengine=io_uring`, `--md_per_io_size`, `--pi_act=0`, `--pi_chk`, app tags, variable block-size ranges, and optional engine flags. `get_lbafs()`, `get_guard_pi()`, `get_capabilities()`, `format_device()`, and `difdix_test()` discover and iterate device formats.

## Control Flow
`main()` parses `--dut`, resolves fio, queries LBA formats and namespace PI capabilities with `nvme-cli`, assigns the target filename to every test, and loops over `(lbaf, pil, pitype)` combinations. Each combination formats the device, creates a combination-specific artifact directory, adjusts block-size range, metadata size, and `pi_chk` for Type 3 PI, then runs five tests covering write/read success and expected read failures for app-tag mismatch or invalid mask.

## State and Persistence Behavior
This script persistently reformats the target namespace and overwrites data on it. Artifacts are written under a timestamped root, partitioned by LBA format, PI location, and PI type. `TEST_LIST` entries are mutated per combination with derived `filename`, `bsrange`, `md_per_io_size`, and `pi_chk`.

## Dependencies and Integration Points
Requires Linux, root/sudo access, `nvme` CLI, a target NVMe namespace, fio with io_uring metadata support, and JSON output parsing through `fiotestlib`.

## Risks
The test is explicitly destructive. It trusts `sudo nvme format` and handles one known rescan warning but skips other failures. It assumes JSON keys from `nvme-cli` such as `lbafs`, `elbafs`, `mc`, and `dpc`. Type 3 PI handling strips `REFTAG`, but other device-specific PI restrictions may still produce false failures.

## Test Signals
Passing signals include successful metadata writes, successful reads with matching guard/ref/app tags, intentional failure for app-tag mismatch, intentional failure for invalid app-tag mask, and compatibility across supported LBA format/PI combinations.
