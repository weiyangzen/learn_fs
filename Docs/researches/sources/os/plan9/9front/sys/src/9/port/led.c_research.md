# File Research: sources/os/plan9/9front/sys/src/9/port/led.c

Common LED state string conversion and simple control-file read/write helpers.

Key responsibilities:
- Maps IBPI LED state enum values to names like `normal`, `locate`, `fail`, and `rebuild`.
- Converts state names back to enum values.
- Implements `ledr()` to read the current LED state as text.
- Implements `ledw()` to parse a control write and update `Ledport.led`.

Dependencies:
- Uses `parsecmd()` and Plan 9 error `Ebadarg`.
- Paired with `led.h`.

Notable risks:
- `ledw()` updates only the software `Ledport` state; hardware application is left to the embedding driver.
