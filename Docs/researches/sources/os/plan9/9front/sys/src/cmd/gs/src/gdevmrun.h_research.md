# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmrun.h

## Role

Public definition of the run-length memory device wrapper.

## Main Contents

- Defines `gx_device_run`, whose first field is `gx_device_memory md`.
- Tracks:
  - `runs_per_line`
  - uninitialized line range `umin/umax1`
  - standardized line range `smin/smax1`
  - saved procedure pointers for operations replaced by run-oriented procedures.
- Declares `gdev_run_from_mem`.

## Design Notes

Because `gx_device_memory` is first, a run device can be treated as a memory device where needed. The saved procedure table makes run encoding an optional wrapper around an already configured memory device.

## Research Notes

Header contract for `gdevmrun.c`; no direct filesystem behavior.
