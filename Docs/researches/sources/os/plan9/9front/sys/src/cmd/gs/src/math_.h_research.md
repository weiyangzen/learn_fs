# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/math_.h

## Purpose
Ghostscript portability wrapper for `math.h`.

## Main Structure
- Includes `std.h`, then either `vmsmath.h` or standard `<math.h>`.
- Defines `M_PI` if missing.
- Defines `degrees_to_radians`, `radians_to_degrees`, and exact `MAX_FLOAT` constants for VAX and IEEE-like platforms.
- Supplies or aliases `hypot` for selected systems.
- Declares `gs_sqrt` and intercepts `sqrt` in `DEBUG` builds.

## Integration Notes
- Used throughout graphics/math-heavy Ghostscript modules via `math__h` dependencies.

## Risks and Edge Cases
- `sqrt` macro interception can surprise code that expects the raw library function under `DEBUG`.
- Fallback `hypot` macro may evaluate arguments more than once through multiplication expressions.
