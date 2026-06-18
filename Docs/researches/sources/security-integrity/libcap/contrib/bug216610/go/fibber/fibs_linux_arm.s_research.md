<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/go/fibber/fibs_linux_arm.s -->
# sources/security-integrity/libcap/contrib/bug216610/go/fibber/fibs_linux_arm.s

## Purpose
ARM Go assembly trampoline for calling C functions embedded in `.syso` objects from Go.

## Important APIs, Types, And Functions
Defines `TEXT ·spacer(SB)` and `TEXT ·syso(SB),$0-8`; loads the function into `R14`, state into `R0`, and branches with link.

## Control Flow
Receives a function pointer and state pointer, maps them to ARM calling convention registers, calls the C function, and returns.

## State And Persistence Behavior
No persistent state beyond C mutation of the provided state pointer.

## Dependencies And Integration Points
Used by bug216610 linux/arm builds with cross-generated `.syso` files.

## Risks And Edge Cases
Manual calling-convention bridging is fragile and architecture-specific. It assumes 32-bit pointer layout and Go assembler frame offsets.

## Test Signals
Signals are successful arm build/link and correct Fibonacci output on target.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/go/fibber/fibs_linux_arm.s -->
