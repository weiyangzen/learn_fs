# sources/test-tools/pynfs/nfs4.0/use_local.py

Purpose: Path bootstrap helper that makes local pynfs modules importable when scripts are run from the source tree rather than an installed package.

Important APIs/types/functions: Imports `sys`, `os`, and `join/split` from `os.path`. It has no functions; all behavior runs at import time.

Control flow: Captures `cwd`, splits it into parent/head, constructs paths for sibling `xdr`, parent RPC area, and current directory, then inserts them into `sys.path[1:1]`.

State and persistence behavior: Mutates only process-local `sys.path`.

Dependencies and integration points: Used by `setup.py` fallback when `xdrgen` import fails. It assumes the current working directory is the `nfs4.0` package root and sibling directories follow the historical pynfs layout.

Risks: The condition is `if True or cwd not in sys.path`, so it always inserts paths and can duplicate entries on repeated imports. It depends on current working directory rather than file location.

Test signals: No direct tests; import success of local `xdrgen`/RPC modules is the practical signal.
