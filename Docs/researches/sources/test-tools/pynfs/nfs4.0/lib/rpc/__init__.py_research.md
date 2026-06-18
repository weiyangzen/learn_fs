<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/lib/rpc/__init__.py -->
# sources/test-tools/pynfs/nfs4.0/lib/rpc/__init__.py

Purpose: package convenience initializer for the pynfs RPC library.

Important APIs/types/functions: executes `from rpc import *` and declares `__all__ = ['rpcsec', 'rpc_const.py', 'rpc_type.py']`. It is intended to expose the top-level RPC module names to older pynfs imports.

Control flow/state: import-time only; no persistent state beyond whatever the imported `rpc` module initializes.

Dependencies/integration: depends on Python import path layout where `rpc` resolves to the local package/module set. It supports legacy code that imports from `rpc` directly.

Risks/test signals: the `__all__` entries include `.py` suffixes, which is unusual for Python packages and may not behave as intended with `from rpc import *`. Import errors are the only direct signal.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/lib/rpc/__init__.py -->
