<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/clirap2.c -->
# sources/user-network-fs/samba/source3/utils/clirap2.c

## Purpose
`clirap2.c` implements additional client-side RAP (Remote Administration Protocol) calls over SMB transaction `\PIPE\LANMAN`. These functions support legacy management operations for groups, users, open files, shares, servers, print queues, services, sessions, and connections, mainly for Samba's `net rap` and related utilities.

## Important APIs, types, and functions
- Buffer helpers and macros (`PUTBYTE`, `GETWORD`, `PUTSTRING`, `PUTSTRINGP`, `rap_getstring*`, `make_header`) marshal and unmarshal RAP's fixed and pointer-style ASCII structures.
- `cli_api()` wraps `cli_trans()` to send SMBtrans requests and returns heap-duplicated response parameter/data buffers.
- Group APIs include `cli_NetGroupDelete`, `cli_NetGroupAdd`, `cli_RNetGroupEnum`, `cli_RNetGroupEnum0`, `cli_NetGroupDelUser`, `cli_NetGroupAddUser`, `cli_NetGroupGetUsers`, and `cli_NetUserGetGroups`.
- User APIs include `cli_NetUserDelete`, `cli_NetUserAdd`, `cli_RNetUserEnum`, and `cli_RNetUserEnum0`.
- File/share/server APIs include `cli_NetFileClose`, `cli_NetFileGetInfo`, `cli_NetFileEnum`, `cli_NetShareAdd`, `cli_NetShareDelete`, `cli_get_pdc_name`, and `cli_get_server_name`.
- Print/service/session/connection APIs include `cli_NetPrintQEnum`, `cli_NetPrintQGetInfo`, `cli_RNetServiceEnum`, `cli_NetSessionEnum`, `cli_NetSessionGetInfo`, `cli_NetSessionDel`, and `cli_NetConnectionEnum`.

## Control flow
Each public function constructs a RAP parameter block with an API number, request format string, response format string, and fixed arguments. Calls that send structured records also build a data block with fixed fields and pointer offsets into a free-string area. `cli_api()` sends the SMB transaction, then the caller checks the 16-bit RAP result code, decodes converter/count values from response parameters, walks returned records in `rdata`, converts strings into local memory, and invokes a caller-supplied callback for each returned item.

## State and persistence behavior
The file itself keeps no global state. Remote state changes occur on the target SMB server: creating/deleting users and groups, adding/removing group members, closing files, adding/deleting shares, deleting sessions, and similar management operations. Memory returned from `cli_api()` is freed in each function with `SAFE_FREE`; transient talloc frames hold converted strings while callbacks run.

## Dependencies and integration points
It depends on `struct cli_state`, `cli_trans()`, RAP constants and structs from generated `rap.h`, service constants, Samba string conversion helpers, little-endian access macros, overflow/range helpers, and callback signatures declared in `clirap2.h`. `net rap` command modules are the primary consumers.

## Risks and edge cases
- RAP is legacy, ASCII-oriented, and limited by 16-bit counts and caller-provided buffer sizes; many functions note incomplete `ERRmoredata` resume handling.
- Manual marshalling uses fixed arrays and pointer arithmetic; every bounds check around `endp` matters.
- Some callbacks ignore the `state` parameter and pass `cli` instead in older functions, preserving historical behavior but surprising new callers.
- Error reporting maps only selected numeric RAP errors to messages.
- A few code paths show duplicated local declarations or duplicated `if (res == 0)` blocks, so this file benefits from compiler warnings and focused tests.

## Test signals
Remote integration tests using `net rap` against Samba or compatible SMB servers are the main validation signal. Useful checks include group/user add/delete/enumerate, file/session listing, share add/delete, PDC discovery, print queue enumeration, and malformed/large response handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/clirap2.c -->
