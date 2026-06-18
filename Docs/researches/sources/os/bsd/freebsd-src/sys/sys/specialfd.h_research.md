# File Research: sources/os/bsd/freebsd-src/sys/sys/specialfd.h

## Purpose
`specialfd.h` defines the small argument ABI for the `__specialfd` syscall.

## Main Interfaces
- `enum specialfd_type` currently identifies `SPECIALFD_EVENTFD` and `SPECIALFD_INOTIFY`.
- `struct specialfd_eventfd` carries an initial counter value and flags.
- `struct specialfd_inotify` carries creation flags.

## Implementation Notes
This is only a public data-contract header; creation and validation happen in syscall implementation code.

## Dependencies and Constraints
No includes. Values are ABI-visible and must remain stable for userland callers.
