# sources/test-tools/kdevops/workflows/fio-tests/Kconfig

## Purpose
Defines the fio-tests matrix: quick/performance/latency/throughput/mixed/filesystem/multi-filesystem modes, devices, runtime/ramp time, filesystem setup, block sizes, IO depths, jobs, patterns, and graphing options.

## Important APIs, Types, and Functions
Important symbols include `FIO_TESTS_*` mode choices, `FIO_TESTS_DEVICE`, `FIO_TESTS_RUNTIME`, `FIO_TESTS_RAMP_TIME`, filesystem mount/device/label options, multi-fs enable flags, block-size/range flags, IO depth flags, job-count flags, workload flags, `FIO_TESTS_IOENGINE`, result/log settings, and graph settings.

## Control Flow
CLI-detected symbols override runtime/ramp/quick defaults. Modes select A/B and filesystem requirements. Filesystem options source `Kconfig.fs` only when required. Quick mode narrows defaults; multi-filesystem mode exposes per-variant VMs and computes a count.

## State and Persistence Behavior
Choices persist in `.config` and YAML. Runtime results persist under `FIO_TESTS_RESULTS_DIR`; filesystem tests format/mount configured devices.

## Dependencies and Integration Points
Integrates with fio Ansible playbooks, filesystem roles, provider storage symbols, and graphing scripts.

## Risks and Edge Cases
The matrix can become large and long-running. Device defaults are destructive if wrong. `FIO_TESTS_MULTI_FS_COUNT` special-cases only a few combinations and otherwise defaults to `8`. Large block-size/bigalloc options need kernel/tool support.

## Test Signals
Validate quick, performance, filesystem, and multi-filesystem configs. Smoke-test `/dev/null` and disposable filesystem devices. Confirm generated hosts/extra vars match enabled variants.
