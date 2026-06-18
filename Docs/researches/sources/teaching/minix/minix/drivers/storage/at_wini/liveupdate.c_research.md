# File Research: sources/teaching/minix/minix/drivers/storage/at_wini/liveupdate.c

## Purpose
Defines SEF live update readiness policy for the `at_wini` driver.

## Key Behavior
- Imports global `w_command`.
- Provides helper macros to classify whether a command is pending, read-pending, or write-pending.
- Defines custom live update states:
  - `AT_STATE_READ_REQUEST_FREE`
  - `AT_STATE_WRITE_REQUEST_FREE`
- `sef_cb_lu_prepare()` permits:
  - standard request/protocol-free states only when no command is pending;
  - read-free when no read command is pending;
  - write-free when no write command is pending.
- `sef_cb_lu_state_isvalid()` accepts SEF standard states and the two custom states.
- `sef_cb_lu_state_dump()` reports current command and readiness for standard and custom states.

## Integration Notes
Registered by `at_wini.c` during SEF startup. It uses ATA command constants from `at_wini.h`.

## Risks
Readiness is based only on `w_command`, so correctness depends on all command paths setting `CMD_IDLE` reliably after completion or failure.
