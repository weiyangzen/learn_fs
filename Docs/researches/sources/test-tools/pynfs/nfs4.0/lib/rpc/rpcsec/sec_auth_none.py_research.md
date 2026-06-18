<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/lib/rpc/rpcsec/sec_auth_none.py -->
# sources/test-tools/pynfs/nfs4.0/lib/rpc/rpcsec/sec_auth_none.py

Purpose: concrete AUTH_NONE security flavor for pynfs RPC.

Important APIs/types/functions: `SecAuthNone` subclasses `SecFlavor` without overrides, inheriting AUTH_NONE credentials, AUTH_NONE verifiers, identity data wrapping, and no verifier checks.

Control flow/state: stateless. Every RPC call uses an empty AUTH_NONE opaque auth.

Dependencies/integration: used by `rpc.py` as the default security flavor when no `sec_list` is provided.

Risks/test signals: appropriate only for servers that accept unauthenticated RPC. Authentication failures will surface as RPC denied/accepted errors from the client layer, not inside this class.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/lib/rpc/rpcsec/sec_auth_none.py -->
