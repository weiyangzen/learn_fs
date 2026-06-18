# File Research: sources/os/plan9/9front/sys/src/cmd/cifs/nterrstr.c

Large NTSTATUS-to-string mapping table plus formatter. The table includes success/warning/error statuses across core NT, filesystem, network, DFS, Kerberos, smart card, cluster, ACPI, Side-by-Side, Terminal Services, and related facilities.

Several entries are adjusted to match Plan 9/APE-style user-facing errors, for example mapping access/object path failures to messages like `permission denied`, `does not exist`, or `file name syntax`.

`nterrstr(uint err)` derives the NTSTATUS facility from bits 16..26, maps selected facility names, scans the table for an exact status code, prefixes non-error statuses with `warning, `, and returns a static formatted string.

Used for CIFS packet/RPC error reporting when the server negotiates NT error codes (`FL2_NT_ERRCODES`).

Implementation note: linear lookup over a large static table is simple and acceptable for error paths/debug output; return storage is static and not reentrant.
