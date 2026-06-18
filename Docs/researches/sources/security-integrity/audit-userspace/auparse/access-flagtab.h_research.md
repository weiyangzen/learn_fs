# sources/security-integrity/audit-userspace/auparse/access-flagtab.h

Purpose: Source table mapping `faccessat`/access-related AT_* flag bit values to symbolic names for auparse interpretation.

Important APIs, types, and functions: Contains `_S(value, name)` macro rows for `AT_SYMLINK_NOFOLLOW`, `AT_EACCESS`, and `AT_EMPTY_PATH`. It is consumed by `gen_access-flagtabs_h` in `auparse/Makefile.am` to generate `access-flagtabs.h`.

Control flow: No executable flow. Build-time generator includes the file with `_S` defined to emit translation data.

State and persistence: Static build-time data only. Generated output persists in the build tree.

Dependencies and integration points: Values are documented as coming from `fcntl.h`. The generated table feeds auparse field interpretation for access/openat-family flags.

Risks and edge cases: If kernel/libc adds new access flags, interpretations will be incomplete until this table is updated. Duplicate or wrong numeric values would produce misleading audit interpretations.

Test signals: Coverage is indirect through generated table builds and any auparse interpretation tests that inspect access flag names.
