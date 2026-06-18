# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_device.h

## Purpose

`emlxs_device.h` defines the global driver control structure for the Emulex FCA driver.

## Main Types

`emlxs_device_t` tracks:

`hba_count`: number of active HBAs.

`hba[MAX_FC_BRDS]`: pointers to HBA instances.

`lock`: global device lock.

`drv_timestamp` and `log_timestamp`: driver/log timing metadata.

`log[MAX_FC_BRDS]`: per-board message log pointers.

Conditional dump file pointers for text, dump, and CEE dump files are present under `DUMP_SUPPORT`.

## Research Notes

The comment states this structure must match `./mdb/msgblib.c`, indicating debugger/tooling ABI coupling. It is global driver state rather than per-I/O state, but it coordinates all FC adapter instances visible to the driver.
