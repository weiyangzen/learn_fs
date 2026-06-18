# File Research: sources/local-fs/mtd-utils/tests/ubi-tests/stress-test.sh

## Role
High-level UBI test stress orchestrator over simulated MTD geometries.

## Main Behavior
- Sets `PATH` so test scripts and mtd-utils tools are found.
- Cleans up `ubi`, `nandsim`, and `mtdram` modules on exit/signals.
- Runs `runtests.sh /dev/ubi0` across `mtdram` and `nandsim`, fastmap enabled/disabled, VID header offset factor 0/1, and many flash/PEB/page sizes.
- Loads simulated devices, attaches UBI with `modprobe ubi mtd=...`, runs tests, then unloads modules.

## Interfaces And Dependencies
- Uses `/proc/mtd`, `modprobe`, `rmmod`, `modinfo`, `load_nandsim.sh`, and `runtests.sh`.
- Requires kernel modules `nandsim`, `mtdram`, and `ubi`.

## Notes
- `runtests.sh` failures are ignored with `||:` inside `run_test`, so the full sweep continues even after a failed test run.
- Uses `sudo rmmod` in cleanup inside `run_test`, while earlier module operations are unqualified.
