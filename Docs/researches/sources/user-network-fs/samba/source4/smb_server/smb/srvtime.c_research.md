# sources/user-network-fs/samba/source4/smb_server/smb/srvtime.c

## Purpose
Wraps DOS time serialization and parsing helpers so SMB1 command handlers consistently apply the negotiated server time-zone offset stored on the connection.

## Important APIs, Types, And Functions
- `srv_push_dos_date()` writes time/date format with `push_dos_date()`.
- `srv_push_dos_date2()` writes date/time word-reversed format with `push_dos_date2()`.
- `srv_push_dos_date3()` writes the 32-bit "unix-like" DOS format with `push_dos_date3()`.
- `srv_pull_dos_date()`, `srv_pull_dos_date2()`, and `srv_pull_dos_date3()` parse the corresponding formats back to GMT `time_t`.

## Control Flow
Handlers pass the active `smbsrv_connection`, destination/source buffer, offset, and Unix timestamp. These wrappers do not branch beyond selecting the underlying format; they simply pass `smb_server->negotiate.zone_offset`.

## State And Persistence
No state is stored here. The only state consumed is `smb_conn->negotiate.zone_offset`, initialized in `smbsrv_init_smb_connection()` and used throughout the lifetime of the connection.

## Dependencies And Integration Points
Used by negotiation, legacy file info replies, open/read/write metadata handlers, print queue serialization, and Trans2 file/fs info conversions. It depends on the lower-level time helpers declared through Samba includes and on `smb_server.h` for the connection type.

## Risks
The risk is semantic rather than structural: SMB1 legacy time fields are local-time encoded, so using the wrong wrapper or offset shifts file timestamps. DST and zone offset behavior should remain aligned with the lower-level `push_dos_*`/`pull_dos_*` helpers. Because this file is tiny, regressions usually come from call-site misuse.

## Test Signals
Test round trips for all three DOS date formats using nonzero time-zone offsets, timestamps around DST transitions if supported by the lower-level helpers, and representative call sites such as negotiate, getatr, open, setattr, and print queue entries.
