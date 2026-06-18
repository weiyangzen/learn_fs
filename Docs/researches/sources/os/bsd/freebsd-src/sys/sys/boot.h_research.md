# File Research: sources/os/bsd/freebsd-src/sys/sys/boot.h

## Purpose
`boot.h` declares helper functions for converting boot environment and command-line arguments into FreeBSD boot flags.

## Main Interfaces
- `PATH_KERNEL` is `/boot/kernel/kernel`.
- Functions: `boot_env_to_howto`, `boot_howto_to_env`, `boot_parse_arg`, `boot_parse_cmdline_delim`, `boot_parse_cmdline`, and `boot_parse_args`.

## Implementation Notes
This header is a small shared interface between boot parsing code and consumers that need to translate text/environment configuration to `howto` flags.

## Dependencies and Constraints
No includes are required by this header. Implementations are external.
