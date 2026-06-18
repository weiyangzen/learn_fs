# sources/security-integrity/audit-userspace/auparse/auparse-defs.h

Purpose: Public ABI definitions for libauparse source modes, search modes, event metadata, callback event kinds, field types, escape modes, destroy modes, and normalization options.

Important APIs, types, and functions: Defines `ausource_t`, legacy `ausearch_op_t`, `austop_t`, `ausearch_rule_t`, `au_event_t`, `auparse_cb_event_t`, `auparse_type_t`, `auparse_esc_t`, `auparse_destroy_what_t`, and `normalize_option_t`. `auparse_type_t` carries an explicit "ONLY APPEND" ABI warning.

Control flow: No runtime control flow. These enums and structs shape behavior in `auparse.c`, `expression.c`, interpretation code, and public callers.

State and persistence: No mutable state. ABI persistence is important: enum order and struct layout are part of the installed library contract.

Dependencies and integration points: Included by `auparse.h` and internal auparse files. C++ linkage guards allow use from C++ callers.

Risks and edge cases: Changing or reordering enum values can break ABI or caller assumptions. `au_event_t.host` is a const pointer with ownership dependent on context; callers must follow the accessor contracts in `auparse.h`.

Test signals: ABI checks, compilation of public consumers, and parser tests that classify field types are the main signals.
