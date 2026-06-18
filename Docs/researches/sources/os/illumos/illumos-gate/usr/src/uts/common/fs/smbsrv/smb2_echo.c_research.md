# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_echo.c

Read completely. This is the SMB2 `ECHO` command handler.

`smb2_echo()` decodes the request structure as `StructSize` plus reserved field, requires `StructSize == 4`, emits DTrace start/done probes, and encodes a minimal SMB2 Echo response with structure size 4 and reserved zero. It does not require user or tree context; that suppression is configured in `smb2_dispatch.c`.

The file has no filesystem dependencies and only includes `smbsrv/smb2_kproto.h`. Its primary purpose is connection liveness/protocol keepalive handling.
