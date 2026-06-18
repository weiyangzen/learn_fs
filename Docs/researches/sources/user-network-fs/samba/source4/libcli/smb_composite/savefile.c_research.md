<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/smb_composite/savefile.c -->
# sources/user-network-fs/samba/source4/libcli/smb_composite/savefile.c

Purpose: implements an async whole-file write over SMB1 using open/create-if-needed, repeated WriteX, and close.

Important APIs and types: `enum savefile_stage`, `struct savefile_state`, `smb_composite_savefile_send`, `smb_composite_savefile_recv`, `smb_composite_savefile`, `savefile_open`, `savefile_write`, `savefile_close`, and `setup_close`. It uses raw open/write/close requests.

Control flow: `send` opens `io->in.fname` with write-data access, normal attributes, shared read/write, `NTCREATEX_DISP_OPEN_IF`, and anonymous impersonation. After open it closes immediately for size zero. Otherwise it writes chunks sized to `max_xmit - 100`, accumulating `total_written`. A short write or reaching the requested size triggers close; close completion verifies `total_written == io->in.size`.

State and persistence: state tracks the open handle through the raw request structs and stores only `total_written`; remote persistence is the target file contents. There is no explicit truncation before writing, so rewriting a shorter buffer over an existing longer file may leave trailing data unless server disposition semantics are changed elsewhere.

Risks: the lack of truncation is the main data-integrity concern. Partial writes are converted to close then `NT_STATUS_DISK_FULL` if incomplete. Test signals include creating new files, overwriting longer files, zero-byte saves, max_xmit chunking, disk-full simulation, and close error handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/smb_composite/savefile.c -->
