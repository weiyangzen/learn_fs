<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/lib/rpc/rpcsec/__init__.py -->
# sources/test-tools/pynfs/nfs4.0/lib/rpc/rpcsec/__init__.py

Purpose: empty package marker for pynfs RPC security flavors.

Important APIs/types/functions: no runtime definitions are present. The package contains `base.py`, `sec_auth_none.py`, `sec_auth_sys.py`, and optional GSS support modules.

Control flow/state: import has no side effects.

Dependencies/integration: enables relative imports such as `.base` and `.sec_auth_gss` from the RPC layer.

Risks/test signals: none beyond package discovery. An empty initializer keeps security flavor modules independently loadable.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/lib/rpc/rpcsec/__init__.py -->
