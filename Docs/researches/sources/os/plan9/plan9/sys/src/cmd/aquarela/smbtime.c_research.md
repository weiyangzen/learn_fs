# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbtime.c

Provides conversion between Plan 9 Unix-like seconds, DOS packed date/time, NT FILETIME, and SMB UTC-like time values.

Key points:
- `smbplan9time2datetime` converts seconds plus timezone offset into DOS date/time bitfields.
- `smbdatetime2plan9time` converts DOS date/time back to seconds using a GMT `Tm`.
- `smbplan9time2time` and `smbtime2plan9time` convert to/from NT 100 ns ticks since 1601-01-01.
- `smbplan9time2utime` and `smbutime2plan9time` apply timezone offsets for SMB time fields.

Dependencies:
- Uses Plan 9 `Tm`, `gmtime`, `tm2sec`, and SMB logging.

Notable behavior:
- DOS seconds have 2-second granularity.
- Offset handling is explicit and sign-sensitive.
