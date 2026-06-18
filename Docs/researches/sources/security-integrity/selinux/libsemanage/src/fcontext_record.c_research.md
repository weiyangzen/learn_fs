# sources/security-integrity/selinux/libsemanage/src/fcontext_record.c

Purpose: implements libsemanage's native file-context record object because file-context records are not simple direct aliases to a sepol record type. A record stores a matching expression, object type, and optional SELinux context.

Important APIs/types/functions: defines `struct semanage_fcontext` and `struct semanage_fcontext_key`; implements key create/extract/free, `semanage_fcontext_compare`, `semanage_fcontext_compare2`, creation, expression setters/getters, type setters/getters, `semanage_fcontext_get_type_str`, context setters/getters, clone/free, and `SEMANAGE_FCONTEXT_RTABLE`.

Control flow: key creation duplicates expression strings and records the object type. Comparisons sort by expression first and type second. `semanage_fcontext_create` initializes type to `SEMANAGE_FCONTEXT_ALL`; setters duplicate or clone owned data. `semanage_fcontext_clone` constructs a fresh record then deep-copies expression and context.

State/persistence: records are heap-owned; expression and context ownership is internal to the record after setters. Persistence is indirect through file/local/policy database tables. Dependencies include `debug.h`, `semanage_context_clone/free`, and the generic `record_table_t` contract.

Risks: NULL input is mostly not guarded, so callers must provide valid expressions and contexts. `set_con` clones the input context, so callers must still free their original. Tests should cover deep-copy behavior, key comparison order, `<<none>>` context handling through file parsing, and all object-type string mappings.
