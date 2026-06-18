# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/hdio.h

## Role

`hdio.h` defines legacy hard-disk ioctl data structures and command codes for generic commands, drive information, bad-sector maps, diagnostics, and error logs.

## Key Interfaces and Data

- `hdk_cmd` describes a command, flags, block number, sector count, user buffer, and buffer length.
- `hdk_type` reports/sets drive type metadata: hard sector count, PROM revision, controller-specific type, and status.
- `hdk_badmap` points to a user bad-sector map buffer.
- Execution flags include silent, diagnose, isolate, read, write, and kernel-buffer modes.
- `hdk_diag` reports most recent command, sector, error number, and severity.
- `hdk_loghdr` describes an error-log table buffer.
- `hdk_log` records block, failure count, type, and primary/secondary errors.
- Log type flags distinguish soft and hard errors.
- Severity values range from no error to fatal.
- Media error types distinguish media from non-media failures.
- Defines `HDKIOC*` ioctl command numbers for set/get drive type, set/get bad map, generic command, and diagnostics.

## Dependencies and Use

The header is a historical disk-driver ABI. It does not include modern block-layer abstractions.

## Research Notes

Several comments indicate aging design issues, such as error codes being specified in drivers instead of centralized in this header.
