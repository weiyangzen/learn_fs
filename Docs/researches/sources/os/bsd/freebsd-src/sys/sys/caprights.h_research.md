# File Research: sources/os/bsd/freebsd-src/sys/sys/caprights.h

## Purpose
`caprights.h` defines the storage type for Capsicum descriptor rights and declares common kernel right sets.

## Main Interfaces
- Defines `CAP_RIGHTS_VERSION_00` and current `CAP_RIGHTS_VERSION`.
- `struct cap_rights` stores rights words in `cr_rights[]`; version 0 uses two `uint64_t` words.
- Declares `cap_rights_t`.
- Kernel builds declare many predefined const right sets, such as read, write, seek, mmap, ioctl, fcntl, socket, process descriptor, and VFS operation rights.

## Implementation Notes
The bit layout reserves high bits for version and index metadata. The version plus array-size encoding allows future extension while retaining compact fixed ABI for version 0.

## Dependencies and Constraints
The header itself does not include other headers for `uint64_t`, so consumers must have suitable type context. Predefined right constants are only declared under `_KERNEL`.
