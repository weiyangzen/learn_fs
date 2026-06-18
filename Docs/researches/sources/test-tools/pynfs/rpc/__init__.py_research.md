# sources/test-tools/pynfs/rpc/__init__.py

Purpose: package initializer for the RPC package.

Important APIs/types/functions: `from rpc import *` and `__all__ = ["rpc"]`.

Control flow: imports the top-level `rpc` module into package namespace at import time.

State and persistence behavior: import side effects only; no persistence.

Dependencies/integration: intended to expose RPC helpers to pynfs modules, but the absolute import style can be sensitive to `sys.path` layout.

Risks and test signals: `from rpc import *` may resolve a top-level module rather than relative `.rpc` under Python 3 packaging semantics, depending on path setup. The local `use_local` shims likely mask this in development.
