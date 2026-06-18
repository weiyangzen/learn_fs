# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/transnt.c

Implements SMB_COM_NT_TRANSACT for security descriptor queries. Helpers build NT transaction headers, fill 32-bit parameter/data counts and offsets, dispatch via `cifsrpc`, and position returned data.

`TNTquerysecurity` requests owner and group security information for a file handle, parses the returned security descriptor, converts binary SID fields to textual `S-...` form, and returns allocated owner/group SID strings. Used by `sid2name.c`.
