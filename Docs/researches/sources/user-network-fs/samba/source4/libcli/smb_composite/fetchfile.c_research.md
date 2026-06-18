<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/smb_composite/fetchfile.c -->
# sources/user-network-fs/samba/source4/libcli/smb_composite/fetchfile.c

Purpose: composes a remote connection and whole-file load into one async operation for fetching a named file from an SMB share.

Important APIs and types: `enum fetchfile_stage`, `struct fetchfile_state`, `smb_composite_fetchfile_send`, `smb_composite_fetchfile_recv`, `fetchfile_connect`, and `fetchfile_read`. It reuses `smb_composite_connect_send` and `smb_composite_loadfile_send`.

Control flow: `send` builds a `smb_composite_connect` from the fetchfile input fields, disables anonymous fallback, copies SMB and session options, then starts a full connect. After connect completion, it creates a `smb_composite_loadfile` with `io->in.filename` and reads the file through the connected tree. On read completion it copies data pointer and size to the outer output.

State and persistence: network connection state and file data are talloc-owned under the composite until `recv`. `recv` steals `io->out.data` to the caller. It does not explicitly disconnect the tree; lifetime follows talloc ownership of the composite and loaded buffer.

Risks: the underlying loadfile cap and read behavior define memory exposure. Fetchfile assumes connect output tree is valid and does not retry authentication. Test signals include connect failure propagation, zero-length and non-empty file reads, data ownership after recv, and preserving input options such as resolver and gensec settings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/smb_composite/fetchfile.c -->
