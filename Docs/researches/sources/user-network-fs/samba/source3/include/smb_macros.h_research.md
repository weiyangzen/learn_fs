# sources/user-network-fs/samba/source3/include/smb_macros.h

## Purpose
`smb_macros.h` collects source3 convenience macros for SMB server checks, packet buffer access, share configuration checks, allocation wrappers, stat validity, domain-controller role checks, Kerberos method checks, and array growth helpers.

## Important APIs, Types, and Macros
- Access checks: `CHECK_READ`, `CHECK_READ_SMB2`, and `CHECK_READ_IOCTL` distinguish path references, real I/O fds, read permission, and SMB2 execute-implies-read semantics.
- Connection/share helpers: `IS_IPC`, `IS_PRINT`, `SNUM`, `CAN_WRITE`, `GUEST_OK`, `MAP_HIDDEN`, `IS_VETO_PATH`, and related macros.
- Stat helpers: `VALID_STAT`, `VALID_STAT_OF_DIR`, and `SET_STAT_INVALID`.
- Packet helpers: `smb_buf`, `smb_buf_const`, `smb_buflen`, `smbreq_bufrem`, `smb_offset`, `smb_len`, `smb_setlen`, and large TCP length aliases.
- Error helpers: `ERROR_NT`, `ERROR_BOTH`, `reply_nterror`, `reply_force_doserror`, and `reply_botherror` preserve call-site file and line.
- Allocation helpers: `SMB_MALLOC*`, `SMB_REALLOC*`, `SMB_CALLOC_ARRAY`, `SMB_XMALLOC*`, `SMB_STRDUP`, and `SMB_STRNDUP`; developer builds can poison direct malloc/realloc/calloc/strdup use.
- Dynamic array helpers: `ADD_TO_ARRAY`, `ADD_TO_MALLOC_ARRAY`, and `ADD_TO_LARGE_ARRAY`.

## Control Flow and State
These macros inline policy checks into SMB request paths. Access macros route behavior based on `files_struct` flags, fd availability, access masks, and SMB request flags. Allocation macros change behavior at compile time when `DEVELOPER`/`PARANOID_MALLOC_CHECKER` is enabled, turning direct allocator use into compile-time errors.

## Persistence Behavior
No persistence is implemented. The macros influence operations that read/write files, allocate state, and generate protocol errors.

## Dependencies and Integration Points
This header assumes many Samba-wide symbols are available: `files_struct`, `connection_struct`, `lp_*` configuration accessors, SMB byte accessors (`CVAL`, `SVAL`, `IVAL`), `fsp_get_io_fd`, `error_packet`, `reply_*`, allocator helpers, role constants, and Kerberos method constants. It is included from `smb.h`, making it widely visible.

## Risks
- Macros evaluate arguments in C preprocessor context; callers must avoid side effects where not safe.
- Access-check macros must stay aligned with Windows SMB2 semantics and low-level VFS pathref restrictions.
- The `SMB_VFS_NEXT_FSTATAT`-style typo risk seen in macro-heavy code applies generally here: incorrect identifiers can compile only in some contexts.
- Allocation wrappers assert on growth failures in `ADD_TO_ARRAY`, which is appropriate for internal invariants but not for recoverable external input paths.

## Test Signals
Signals include developer builds with allocator poisoning, SMB2 read/ioctl access torture tests, stat-cache tests, guest/share configuration tests, and packet encoding/decoding coverage for SMB1 paths.
