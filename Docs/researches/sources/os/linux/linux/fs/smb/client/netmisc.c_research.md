# File Research: sources/os/linux/linux/fs/smb/client/netmisc.c

## Purpose
Provides network and time conversion helpers for the CIFS/SMB client, including textual IP parsing, socket port assignment, NT time conversion, Unix-to-NT time conversion, and DOS date/time conversion.

## Main Interfaces
- `cifs_convert_address()` parses IPv4 and IPv6 literals, including IPv6 numeric scope IDs.
- `cifs_set_port()` writes a TCP/UDP port into IPv4 or IPv6 sockaddr structures.
- `cifs_NTtimeToUnix()` converts NT 1601-based 100ns timestamps to `timespec64`.
- `cifs_UnixTimeToNT()` converts Unix `timespec64` to NT time.
- `cnvrtDosUnixTm()` converts SMB/DOS date and time fields to Unix time.

## Control Flow
Address parsing first attempts IPv4, then IPv6, optionally splitting an IPv6 `%scope` suffix and parsing the scope as an integer. NT time conversion subtracts the NTFS epoch offset and handles negative values specially so 32-bit `do_div()` does not receive a negative dividend. DOS time conversion decodes bitfields, clamps invalid month/day values, adjusts for the 1980 epoch and leap years through 2107, then applies the supplied server time offset.

## Integration Points
Used by metadata conversion in inode and readdir paths, connection address parsing, and SMB1/SMB2 protocol helpers.

## Notable Behaviors
- `cifs_inet_pton()` treats backslash as the parsing terminator for UNC-style addresses.
- DOS conversion logs invalid ranges but still clamps and returns a time.
- NT timestamp conversion leaves timezone adjustment to callers.

## Risks And Review Focus
- Time conversion must preserve pre-1970 NT timestamps and 32-bit architecture behavior.
- IPv6 scope parsing accepts only numeric scope IDs up to 12 characters.
