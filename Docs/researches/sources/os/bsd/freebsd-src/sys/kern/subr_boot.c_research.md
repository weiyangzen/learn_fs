# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_boot.c

## Summary
Provides shared boot-option parsing and conversion helpers compiled in both kernel and boot loader contexts.

## Main Responsibilities
- Converts boot environment variables into a reboot/howto bitmask.
- Writes environment variables from a howto bitmask.
- Parses boot command-line switches and environment assignments.
- Parses delimiter-separated command lines and argv-style vectors.

## Key APIs
- `boot_env_to_howto()`: reads `boot_*` environment variables and returns `RB_*` flags.
- `boot_howto_to_env()`: writes `boot_*` variables for set howto bits.
- `boot_parse_arg()`: parses a single switch group or `name=value` assignment.
- `boot_parse_cmdline_delim()`, `boot_parse_cmdline()`: parse command strings.
- `boot_parse_args()`: parse argv arrays.

## Important Behavior
The same source supports kernel and loader builds by mapping `SETENV`, `GETENV`, and `FREE` to `kern_setenv()`/`kern_getenv()`/`freeenv()` or loader `boot_setenv()`/`getenv()`.

Recognized switches include askname, CD-ROM, debugger/GDB, multiple consoles, mute flags, serial console, pause, probe, default root, single-user, verbose, and `-S` serial speed. Non-switch arguments set environment variables; arguments without `=` get value `"1"`.

Environment variables named in `howto_names` are considered enabled unless their value is exactly `"no"` case-insensitively.

## Dependencies
Uses reboot flag definitions, boot environment interfaces, string helpers, and TSLOG annotations.

## Risks
`boot_parse_arg()` copies environment assignments into a fixed 128-byte buffer, so long assignments are truncated by `strlcpy()`. The `-S` switch consumes the rest of the current argument as `comconsole_speed`.
