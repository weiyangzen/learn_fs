# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_optstr.c

## Purpose
Parses kernel option strings of the form `key=value key2=value2` and extracts values as strings, numbers, or Ethernet MAC addresses.

## Main Entry Points
- `optstr_get()` copies a matched value into a caller buffer.
- `optstr_get_string()` returns a pointer into the original option string.
- `optstr_get_number()`, `optstr_get_number_hex()`, and `optstr_get_number_binary()` parse values in base 10, 16, and 2.
- `optstr_get_macaddr()` is compiled when `NETHER > 0` and parses an Ethernet address through `ether_aton_r()`.

## Control Flow And State
The private `optstr_get_pointer()` skips leading spaces and tabs, scans words separated by spaces, matches an exact key immediately followed by `=`, and returns a pointer to the value after the equal sign. It does not allocate or mutate state. String copy stops at space or NUL and always writes a terminating NUL if the key is found.

Numeric helpers call `strtoul` with the requested base and fail if no digits were consumed. The MAC helper parses into a temporary array before copying to the caller output.

## Dependencies
Uses `<sys/optstr.h>`, kernel string helpers, `strtoul`, and optionally Ethernet parsing/types when network Ethernet support is present.

## Risks And Notes
The scanner treats only spaces as separators after the initial tab-skip logic; tabs inside the option list are not skipped as separators. `optstr_get_string()` returns a pointer into the original string and does not bound the value length. Numeric parsers do not require the whole value token to be consumed, so trailing nonnumeric characters after at least one digit are accepted.
