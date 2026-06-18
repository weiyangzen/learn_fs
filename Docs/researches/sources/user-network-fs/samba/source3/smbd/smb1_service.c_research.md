# sources/user-network-fs/samba/source3/smbd/smb1_service.c

### Purpose
`smb1_service.c` opens SMB1 tree connections to configured shares. It translates a client-supplied service name and device type into a Samba service number, allocates `smbXsrv_tcon` and `connection_struct` state, enforces per-share limits, and delegates share initialization to common connection code.

### Important APIs, Types, And Functions
- `make_connection_smb1()` is the internal constructor for a known service number. It checks `lp_max_connections()`, creates an SMB1 tcon with `smb1srv_tcon_create()`, allocates a `connection_struct` via `conn_new()`, links `conn->cnum` and `conn->tcon`, calls `make_connection_snum()`, then stores the connection under `tcon->compat`.
- `make_connection()` is the exported SMB1 tree-connect entry point. It validates root execution assumptions, open connection count, and session presence; handles `[homes]`; normalizes service names; resolves services with `find_service()`; rejects missing IPC/ADMIN access and DFS proxy shares; and calls `make_connection_smb1()`.

### Control Flow
The public function starts from `req->session` and `service_in`. `[homes]` has fast paths based on `session->homes_snum`, avoiding repeated passwd/winbind lookup. Other services are duplicated, lowercased, and resolved. Invalid or intentionally hidden services return NTSTATUS failures. Successful resolution passes through the internal constructor, which allocates the tcon before the compatibility `connection_struct`, then calls the common share attach logic.

### State And Persistence Behavior
The file creates in-memory tree connection state only. It increments the server's live tcon/connection set by allocating an `smbXsrv_tcon` and `connection_struct`, sets `conn->cnum` to the wire tree id, assigns `conn->tcon`, and marks `tcon->status = NT_STATUS_OK` after `make_connection_snum()` succeeds. On failure it frees partially created tcon/connection state. It reads configuration and live connection counts but does not write persistent files.

### Dependencies And Integration Points
It depends on Samba loadparm share lookup, connection accounting, session state from SMB1 session setup, `smbXsrv_tcon` management, common `make_connection_snum()` share setup, `[homes]` registration done during session setup, DFS proxy configuration, and remote-address/debug helpers.

### Risks
- `make_connection()` assumes it is called as root in normal mode and panics otherwise; callers must preserve privilege expectations.
- The `[homes]` path relies on `session->homes_snum` being created during session setup; regressions there surface as bad network name on tree connect.
- Tcon and connection allocation are split; failure cleanup must keep ownership correct to avoid dangling `tcon->compat` or leaked tcon ids.
- Service name lowercasing and `find_service()` mutation require care with talloc ownership and NULL handling.

### Test Signals
Useful tests include SMB1 tree connect to normal shares, `[homes]` by literal name and concrete username share, unknown shares, IPC$/ADMIN$ refusal paths, `max connections` enforcement, DFS proxy refusal for non-DFS clients, and failure-injection/valgrind coverage around tcon allocation and `make_connection_snum()` failure cleanup.
