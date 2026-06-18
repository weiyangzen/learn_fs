<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/lib/rpc/rpcsec/sec_auth_sys.py -->
# sources/test-tools/pynfs/nfs4.0/lib/rpc/rpcsec/sec_auth_sys.py

Purpose: AUTH_SYS security flavor implementation for pynfs RPC, packing UNIX-style machine, uid, gid, and supplemental groups into the RPC credential body.

Important APIs/types/functions: `SecAuthSys.__init__()` validates machinename length <=255 and gid array length <=16, then uses `xdrlib`/`xdrlib3.Packer` to pack stamp, machinename, uid, gid, and group array. `make_cred()` returns `opaque_auth(AUTH_SYS, self.cred)`. `get_owner()` and `get_group()` expose uid/gid for server-side ownership checks.

Control flow/state: credential bytes are created once at object construction and reused for each call. No verifier override is provided, so the base AUTH_NONE verifier is used.

Dependencies/integration: consumed by `nfs4lib.AuthSys` as the default NFSv4 client security object. Depends on generated RPC constants/types and XDR packing.

Risks/test signals: the default `gids=[]` is mutable but not modified. Packing errors are wrapped in `SecError`; authentication failures later appear as RPC auth errors from the server.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/lib/rpc/rpcsec/sec_auth_sys.py -->
