# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/nterrstr.c

Large NTSTATUS-to-string table plus `nterrstr`. Some messages are intentionally changed to match Plan 9/APE error phrasing, for example permission/not-found style errors.

`nterrstr` derives the NT facility from status bits, labels warnings when the high error bit is not set, searches the table, and returns a formatted message or unknown-code fallback. Used by `cifsrpc` for servers negotiating `FL2_NT_ERRCODES`.
