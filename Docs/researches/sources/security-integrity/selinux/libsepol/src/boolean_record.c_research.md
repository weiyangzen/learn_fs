# sources/security-integrity/selinux/libsepol/src/boolean_record.c

Purpose: Implements the opaque public boolean record and key API.

Important APIs and functions: Implements key create/unpack/extract/free, compare/compare2, name get/set, value get/set, record create/clone/free.

Control flow: Create functions allocate structures and duplicate names. Setters replace owned strings. Clone creates a new record and deep-copies name/value. Key extraction builds a key from a record name.

State and persistence: `struct sepol_bool` owns `char *name` and `int value`; `struct sepol_bool_key` owns `char *name`. No policydb state is changed here.

Dependencies and integration points: Uses `boolean_internal.h`, `debug.h`, libc allocation/string helpers, and handle-based diagnostics. Consumed by `booleans.c` and external callers.

Risks: `sepol_bool_set_value` accepts any int; policydb update rejects non-0/1 later. Null names passed to strdup would crash.

Test signals: Allocation failure handling, clone deep copy, compare ordering, key extraction, and invalid value rejection through `sepol_bool_set` are useful tests.
