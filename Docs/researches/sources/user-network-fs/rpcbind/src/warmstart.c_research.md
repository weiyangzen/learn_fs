<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/warmstart.c -->
# sources/user-network-fs/rpcbind/src/warmstart.c

Purpose: Implements warm-start persistence for rpcbind registrations by writing and reading XDR-encoded registration lists under `RPCBIND_STATEDIR`.

Important APIs, types, and functions: Public functions are `mkdir_warmstart`, `write_warmstart`, and `read_warmstart`. Internal helpers `write_struct` and `read_struct` serialize or deserialize arbitrary XDR list structures. Files are `rpcbind.xdr` for `list_rbl` and, with `PORTMAP`, `portmap.xdr` for `list_pml`.

Control flow: `write_warmstart` ensures the state directory exists and writes `list_rbl` plus optional `list_pml`. `read_warmstart` decodes temporary lists, appends non-rpcbind registrations to the current in-memory lists, and discards stale self-registrations so current transport setup remains authoritative. `read_struct` unlinks the state file after success or non-ENOENT failure, making warm-start files one-shot recovery inputs.

State and persistence: This is the daemon's on-disk persistence layer. Files are written with `umask(077)` to restrict permissions. `mkdir_warmstart` creates the directory with mode 0770 and attempts to chown it to the post-drop user via an `O_DIRECTORY | O_NOFOLLOW` fd.

Dependencies and integration points: Depends on global `list_rbl` and optional `list_pml`, XDR routines `xdr_rpcblist_ptr` and `xdr_pmaplist_ptr`, `RPCBIND_STATEDIR`, and daemon shutdown/abort paths in `rpcbind.c`.

Risks: Files are opened with `fopen("w")`, not an atomic temp-and-rename sequence, so crashes can leave partial XDR. The fallback that closes fds 0 through 9 before retrying write is unusual and could affect diagnostics. Directory creation and chown errors are logged but not fatal. Warm-start data may still be stale for services that did not survive daemon restart; later GETADDR cleanup handles some stale entries.

Test signals: Validate write/read round trips for RPCB and PMAP lists, absence of files, corrupt XDR files, directory creation with expected ownership, one-shot unlink behavior, and filtering of RPCBPROG/PMAPPROG self-registrations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/warmstart.c -->
