# sources/security-integrity/selinux/libselinux/src/label_x.c

Purpose: Implements the X object labeling backend for properties, extensions, clients, events, selections, and poly variants.

Important APIs/types/functions: `selabel_x_init()` installs close, lookup, and stats callbacks. `process_line()` maps type strings such as `property`, `extension`, `client`, `event`, `selection`, `poly_property`, and `poly_selection` to `SELABEL_X_*` constants. Lookup uses `fnmatch()`.

Control flow: init selects `SELABEL_OPT_PATH` or default `selinux_x_context_path()`, verifies a regular file, performs two-pass count/populate parsing, records digest, and generates hash. Lookup scans specs for matching type and pattern, then returns the record and increments matches.

State and persistence: per-handle spec array and match counts persist until close.

Dependencies and integration: optional backend controlled by `NO_X_BACKEND`; frontend handles context validation and translation.

Risks and test signals: invalid type strings are skipped, not fatal. Tests should cover every supported type, wildcard matching, malformed lines, optional backend disablement, digest, and stats.
