# sources/user-network-fs/samba/source3/torture/test_nttrans_fsctl.c

Purpose: This file probes NT transaction FSCTL handling for several control codes and expected statuses. It creates a file, marks it delete-on-close, then sends raw `SMBnttrans` `NT_TRANSACT_IOCTL` requests through `cli_trans()`.

Important APIs/types/functions: The public entrypoint is `run_nttrans_fsctl()`. It uses `cli_nttrans_create()`, `cli_nt_delete_on_close()`, and repeated `cli_trans()` calls. FSCTLs include `FSCTL_SET_SPARSE`, `FSCTL_CREATE_OR_GET_OBJECT_ID`, `FSCTL_GET_REPARSE_POINT`, `FSCTL_SET_REPARSE_POINT`, `FSCTL_GET_SHADOW_COPY_DATA`, `FSCTL_FIND_FILES_BY_SID`, `FSCTL_QUERY_ALLOCATED_RANGES`, and `FSCTL_IS_VOLUME_DIRTY`.

Control flow: After creating `fsctltest`, the test fills the NT transaction setup array with the FSCTL code, fnum, and ioctl marker, then sends data/parameter buffers sized to trigger expected behavior. It frees returned data buffers after object-id and range queries. Each FSCTL has a hard-coded expected NTSTATUS: OK for sparse, object id, allocated ranges; not-a-reparse-point, invalid-buffer-size, or invalid-parameter for others.

State/persistence behavior: Remote state is a temporary file marked delete-on-close. Some FSCTLs can alter file metadata, notably sparse state and object id creation. Returned buffers are talloc-owned and freed locally.

Dependencies and integration points: It depends on SMB1 NT transaction support, FSCTL constants, raw trans helpers, and security access masks. It is an integration test for server ioctl dispatch and status mapping.

Risks: Filesystem support affects FSCTL behavior, especially sparse files, object ids, shadow copies, and allocated ranges. SMB dialect or server feature differences can legitimately alter statuses. Several diagnostic strings mention the wrong FSCTL name after copy/paste, so status is more reliable than message text.

Test signals: Passing is a sequence of exact status checks for each FSCTL and successful cleanup through connection close. Any mismatch prints the actual status and expected status.
