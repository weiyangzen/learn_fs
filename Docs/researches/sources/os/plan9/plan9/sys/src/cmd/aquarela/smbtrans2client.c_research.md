# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbtrans2client.c

Implements client-side SMB TRANS2 request execution and a FIND_FIRST2 helper.

Key points:
- Defines a client transaction method table for `SMB_COM_TRANSACTION2`.
- `smbclienttrans2` fills an `SmbTransaction` from input/output buffers, copies the client protocol header, sets the tree id, and calls `smbtransactionexecute`.
- `smbclienttrans2findfirst2` builds a TRANS2 FIND_FIRST2 request for `SMB_FIND_FILE_BOTH_DIRECTORY_INFO`, sends it, parses returned search metadata, then iterates returned directory entries.

Dependencies:
- Uses `SmbClient`, `SmbTransaction`, transaction encoder/decoder helpers, and buffer APIs.

Notable behavior:
- Contains direct `print`/`smblogdata` debug output in the response parsing path.
- Error strings are produced with `smbstringprint`.
