<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/rpc/use_local.py -->
# sources/test-tools/pynfs/rpc/use_local.py

Purpose: local import bootstrap for running/building the `rpc` package directly from the source checkout without installing sibling pynfs components first.

Important behavior: imports `sys`, `os`, and `join/split`; obtains the current working directory; computes its parent; then inserts sibling directories `gssapi`, `xdr`, `ply`, the parent directory containing `rpc`, and the current directory into `sys.path` at index 1.

Control flow: top-level code executes on import. The condition is `if True or cwd not in sys.path`, so path injection always runs. There are no functions or classes.

State and persistence: mutates only in-process Python import state. It does not write files, but its inserted paths persist for the lifetime of the process and affect all subsequent imports.

Dependencies and integration: used by `rpc/setup.py` when `import xdrgen` fails. It assumes the checkout layout has sibling directories under the same parent as `rpc`.

Risks: unconditional `sys.path` mutation can shadow installed modules and introduce order-dependent imports. Duplicate path entries can accumulate across repeated imports. The hard-coded sibling layout is brittle if pynfs is vendored differently. Test signals: execute `python -c 'import use_local, sys; print(sys.path[:8])'` from `rpc` and verify `xdr`/`ply` can be imported without installation.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/rpc/use_local.py -->
