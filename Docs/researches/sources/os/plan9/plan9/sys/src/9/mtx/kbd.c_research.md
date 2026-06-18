# File Research: sources/os/plan9/plan9/sys/src/9/mtx/kbd.c

## Role

i8042 keyboard and auxiliary PS/2 controller driver for the MTX port. It initializes the controller, handles keyboard scan-code input, supports aux mouse command/enable paths, and registers keyboard interrupt handling.

This is input device support, not filesystem code.

## Main Interfaces

- `i8042reset`
- `i8042auxcmd`
- `i8042auxenable`
- `kbdinit`
- Internal helpers:
  - `outready`
  - `inready`
  - `i8042intr`

## Important Behavior

- Polls controller status for input/output readiness.
- Resets and configures the controller command byte.
- Handles key up/down prefixes and scan-code translation through keyboard tables.
- Calls Plan 9 keyboard queue helpers for decoded runes.
- Supports aux device command writes and installs an aux byte callback.
- `kbdinit` initializes keyboard state and enables keyboard/AUX interrupts.

## Dependencies And Assumptions

- Uses standard PC i8042 I/O ports.
- Depends on shared keyboard translation state/functions from the port layer.
- Uses `intrenable` with keyboard and aux IRQs.

## Notable Risks

- Polling timeouts are fixed.
- Scan-code state handling is global and sensitive to prefix/error bytes.
