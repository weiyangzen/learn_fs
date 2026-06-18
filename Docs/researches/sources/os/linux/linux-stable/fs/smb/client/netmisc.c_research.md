# File Research: sources/os/linux/linux-stable/fs/smb/client/netmisc.c

Read status: complete.

## Purpose

Provides small network and time-conversion helpers used by CIFS/SMB protocol code.

## Main Responsibilities

- Parse textual IPv4 and IPv6 addresses into socket address structures.
- Set network ports in IPv4 or IPv6 socket addresses.
- Convert between NT time and Unix `timespec64`.
- Convert DOS date/time fields into Unix `timespec64`.

## Important Functions

- `cifs_inet_pton()`
  - Internal wrapper around `in4_pton()` and `in6_pton()`.
  - Stops parsing on `\` to support UNC-style address substrings.

- `cifs_convert_address()`
  - Tries IPv4 first, then IPv6.
  - Handles IPv6 `%scope_id` suffixes when numeric.
  - Sets the socket family on success and returns 1/0 for success/failure.

- `cifs_set_port()`
  - Sets `sin_port` or `sin6_port` depending on address family.

- `cifs_NTtimeToUnix()`
  - Converts NT UTC time, based on 1601-01-01 in 100 ns units, to Unix seconds/nanoseconds.
  - Handles negative converted times without relying on signed 64-bit division on 32-bit architectures.

- `cifs_UnixTimeToNT()`
  - Converts Unix `timespec64` to NT UTC 100 ns units.

- `cnvrtDosUnixTm()`
  - Converts SMB/DOS packed date and time fields to Unix time with a supplied offset.
  - Validates/clamps basic date fields and accounts for DOS date range leap-year behavior.

## Dependencies

- Uses kernel IP parsing helpers, endian helpers, CIFS debug logging, SMB date/time wire structures, and NT status/error headers.

## Notable Behaviors

- IPv6 scope ids longer than 12 bytes or nonnumeric scope ids are rejected.
- DOS conversion treats invalid day/month values as log-worthy but clamps them rather than failing.
- NT time conversion leaves timezone adjustment to callers.
