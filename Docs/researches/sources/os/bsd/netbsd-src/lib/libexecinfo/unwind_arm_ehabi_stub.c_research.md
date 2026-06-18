# File Research: sources/os/bsd/netbsd-src/lib/libexecinfo/unwind_arm_ehabi_stub.c

## Purpose
Provides ARM EHABI-compatible unwind helper functions when DWARF EH support is not enabled.

## Main Components
- Declares `_Unwind_VRS_Get()` and `_Unwind_VRS_Set()`.
- `_Unwind_GetGR()` reads a core register through VRS.
- `_Unwind_GetIP()` reads register 15 and clears the Thumb bit.
- `_Unwind_GetIPInfo()` returns IP and sets the info flag to zero.
- `_Unwind_SetGR()` writes a core register through VRS.

## Integration
Conditionally built for earm targets by `libexecinfo/Makefile`.

## Risks / Notes
Only compiled when `__ARM_DWARF_EH__` is not defined. Assumes ARM EHABI register numbering and VRS interfaces.
