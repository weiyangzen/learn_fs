# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomopen.c

Central SMB open/create implementation, including classic open, create, OpenAndX, and NTCreateAndX.

Key functions:
- `openfile` maps SMB access/share/create semantics to Plan 9 `open`/`create`, validates directory/file create options, consults shared-file share-deny state, creates `SmbFile`, allocates fid, and returns optional `Dir` and create action.
- `smbcomopenandx` parses `SMB_COM_OPEN_ANDX`, logs mode/share/attribute/ofun details, opens the file, writes response fields, and chains if requested.
- `smbcomopen` handles legacy open.
- `smbcomcreate` handles legacy create with exclusive share and create-if-not-exists semantics.
- `smbcomntcreateandx` maps NT desired access, share access, create disposition, and create options to `openfile`, then returns NT-style metadata.

Interactions:
- Uses `smbsharedfileget`, `smbidmap`, Plan 9 `dirstat`, `open`, `create`, and `dirfstat`.

Notable details:
- Compatibility share mode is rejected as `ERRbadshare`.
- Directory opens create fid entries with `ioallowed = 0`.
- Several comments mark response fields as approximate or uncertain.
