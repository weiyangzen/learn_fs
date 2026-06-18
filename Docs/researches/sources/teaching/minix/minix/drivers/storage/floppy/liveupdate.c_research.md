# File Research: sources/teaching/minix/minix/drivers/storage/floppy/liveupdate.c

## Purpose

Implements floppy-driver SEF live update readiness and state diagnostics.

## Main Entry Points

- `sef_cb_lu_prepare()`: reports whether the driver can enter the requested live update state.
- `sef_cb_lu_state_isvalid()`: accepts standard SEF live update states and the custom motor-off state.
- `sef_cb_lu_state_dump()`: prints driver state and readiness diagnostics.

## Control Flow And State

The file imports `f_busy`, `motor_status`, `f_drive`, and `last_was_write` from `floppy.c`. Standard request/protocol-free states require no pending request. The custom `FL_STATE_MOTOR_OFF` also requires the selected drive motor to be stopped. Dump output reports each condition for operational diagnostics.

## Dependencies

Depends on SEF live update macros, `floppy.h`, and global state exported by `floppy.c`.

## Risks

The readiness logic only checks the current selected drive for motor state. If multiple drive motors could be on, this custom state may not represent all physical activity. The read/write-pending helper macros are defined but not used in readiness checks.
