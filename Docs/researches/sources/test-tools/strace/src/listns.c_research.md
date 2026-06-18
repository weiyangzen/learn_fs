<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/listns.c -->
# sources/test-tools/strace/src/listns.c

Purpose: decodes the Linux `listns` syscall and versioned namespace request structure.
Important APIs/types/functions: `print_ns_id_req`, `SYS_FUNC(listns)`, `struct ns_id_req`, `ns_type`, `listns_user_ns_id`, and `print_array`.
Control flow: entry prints request size and known fields, including sparse fields only when nonzero, plus future nonzero bytes; exit prints returned namespace IDs capped by return value and requested count.
State and persistence behavior: no persistent state. Dependencies and integration points: namespace/fs syscall decoding and xlat tables.
Risks: future struct growth and size underflow can mislead output if not bounded. Test signals: fixtures for null/short requests, nonzero spare fields, and successful returned arrays.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/listns.c -->
