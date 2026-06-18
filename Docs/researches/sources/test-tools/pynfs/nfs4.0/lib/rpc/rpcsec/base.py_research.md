<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/lib/rpc/rpcsec/base.py -->
# sources/test-tools/pynfs/nfs4.0/lib/rpc/rpcsec/base.py

Purpose: base abstraction for RPC authentication/security flavors used by pynfs RPC clients and servers.

Important APIs/types/functions: `SecError` is the common exception. `SecFlavor` defines `_none = opaque_auth(AUTH_NONE, b'')` and default no-op implementations for `initialize()`, `secure_data()`, `unsecure_data()`, `make_cred()`, `make_verf()`, `make_reply_verf()`, `get_owner()`, `get_group()`, and `check_verf()`.

Control flow/state: the base class is stateless and returns AUTH_NONE credentials/verifiers unless a subclass overrides behavior. Data wrapping and unwrapping are identity functions by default.

Dependencies/integration: imports RPC constants and `opaque_auth` XDR type. `rpc.py` treats concrete security flavor objects through this interface.

Risks/test signals: subclasses must obey the same method contracts because RPC header packing calls `make_cred()` before `make_verf()` and server replies call `make_reply_verf()`. Base behavior is suitable only for no-auth paths.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/lib/rpc/rpcsec/base.py -->
