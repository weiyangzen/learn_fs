# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/doserrstr.c

Maps classic SMB DOS/server/hardware error-class codes to readable Plan 9 error strings. The packed key is `(code << 16) | class`. `doserrstr` classifies low-byte error class, searches the static table, and returns either `"class, message"` or an unknown-code string.

Used by `cifsrpc` when the server did not negotiate NT status codes.
