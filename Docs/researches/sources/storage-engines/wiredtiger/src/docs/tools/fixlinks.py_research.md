# sources/storage-engines/wiredtiger/src/docs/tools/fixlinks.py

## Purpose
Post-processes `doxypy` output for WiredTiger Python API documentation so generated comments link back to corresponding C API documentation.

## Important APIs and control flow
`process` applies regex substitutions to stdin text. It rewrites `Proxy of C ... struct` comments into Python wrapper wording plus `@copydoc` references, uppercases generated `wt_*` class references, maps `char` pointer wording to `string`, adds method-level `@copydoc WT_CONNECTION/WT_CURSOR/WT_SESSION::method` references, adds global function `@copydoc ::wiredtiger_*` references, and removes generated handle parameters from comments. Main reads all stdin and writes transformed output.

## State, dependencies, integration, risks
The script is stateless aside from regex processing. It depends on Python regex semantics and exact generated wrapper comment shapes. It integrates in `pyfilter` after `doxypy.py`. Risks are broad regex replacements inside comments, API naming drift, missed modern annotations, and incorrect rewriting if wrapper text changes. Tests should feed representative generated Python binding snippets for connection, cursor, session, struct wrappers, global functions, `char` arguments, and already-qualified C references.
