## sources/security-integrity/attr/tools/getfattr.c

Purpose: modern CLI for listing and dumping Linux xattrs.

Important functions include `encode`, `print_attribute`, `list_attributes`, `do_print`, and `main`. Control flow compiles a name regex, walks paths with symlink/recursive flags, lists xattrs, filters/sorts names, optionally fetches values, encodes as text/hex/base64, strips leading slashes by default, and formats restore-compatible output. State includes global options, warning/error flags, static growing buffers, and compiled regex. Dependencies are Linux xattr syscalls, `walk_tree`, `quote`, `high_water_alloc`, getopt, regex, and gettext. Risks include heuristic text/base64 choice, static buffers, absolute-path warning side effects, regex errors, path mutation display logic, and no retry if xattr list grows between size and fetch. Tests should cover dump/only-values, encodings, recursive walks, symlink handling, regex filtering, and restore round trip with `setfattr`.
