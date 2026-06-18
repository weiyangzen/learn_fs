# sources/test-tools/pynfs/nfs4.1/use_local.py

Purpose: local import-path shim used by pynfs scripts during development so generated/local modules can be imported without installing the package.

Important APIs/types/functions: module-level code only; imports `sys`, `os`, and `join/split`.

Control flow: captures the current working directory, computes its parent, and inserts the sibling `xdr` directory, the parent directory, and the cwd into `sys.path` near the front. The condition is `if True or cwd not in sys.path`, so insertion always happens on import.

State and persistence behavior: mutates process-global `sys.path`; no filesystem writes.

Dependencies/integration: imported by `testclient.py`, `testserver.py`, and `setup.py` fallback paths.

Risks and test signals: unconditional path insertion can duplicate entries and make imports cwd-dependent. It is intentionally labeled as a hack by callers.
