# sources/test-tools/fio/t/zbd/run-tests-against-scsi_debug

## Purpose
`run-tests-against-scsi_debug` prepares a zoned `scsi_debug` device specifically for zbd write-error recovery tests, then runs `test-zbd-support` cases 72 and 73 through multiple access paths.

## Important APIs, Types, and Functions
The script is linear rather than function-oriented. It unloads any existing `scsi_debug`, reloads it with `add_host=1 zbc=host-managed zone_nr_conv=0`, scrapes recent `dmesg` output for the attached SCSI disk name, verifies the block device VPD page mentions `scsi_debug`, locates the matching `scsi_generic` node, and invokes `test-zbd-support`.

## Control Flow and State
State is held in `dev`, `sg`, and `scriptdir`. Three runs are performed: standard engine against `/dev/sdX`, libzbc engine against the block device, and libzbc engine against the SG node. The target tests are `-t 72 -t 73`, which exercise badblock/error-injection recovery paths.

## Dependencies and Integration Points
It depends on root/module access, `modprobe`, kernel `scsi_debug`, `dmesg` output format, sysfs VPD page layout, and the sibling `test-zbd-support`. It integrates with libzbc mode via `-l`.

## Risks and Test Signals
Risks include unreliable device discovery from `dmesg | tail -5`, lack of cleanup after the run, accidental interference with existing scsi_debug instances, and kernel-debugfs availability for later error injection. Signals are VPD verification failure, explicit run banners, and return codes from `test-zbd-support`.
