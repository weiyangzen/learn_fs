# File Research: sources/os/bsd/dragonflybsd/sys/sys/utsname.h

## Summary
Defines `struct utsname` and `uname()` ABI.

## Main Responsibilities
- Defines `SYS_NMLN` as 32.
- Defines fixed-size fields for system name, node name, release, version, and machine.
- Declares userland `uname()` or kernel global `utsname`.

## Important Behavior
All strings are fixed-width 32-byte fields.

## Risks
The small fixed field size is ABI-visible and can truncate modern version or node strings.
