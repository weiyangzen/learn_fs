# File Research: sources/os/bsd/freebsd-src/sys/sys/splash.h

## Purpose
`splash.h` defines a minimal splash image information structure.

## Main Interfaces
- `struct splash_info` exposes width, height, and depth as 32-bit unsigned integers.

## Implementation Notes
This is a compact shared ABI/header for code that needs splash geometry without depending on larger graphics structures.

## Dependencies and Constraints
Includes `sys/types.h` for `uint32_t`.
