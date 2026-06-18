# sources/security-integrity/selinux/libsemanage/src/fcontexts_local.c

Purpose: exposes local file-context modification APIs over the generic database layer. This is the write-side surface for local fcontext overrides.

Important APIs/functions: `semanage_fcontext_modify_local`, `del_local`, `query_local`, `exists_local`, `count_local`, `iterate_local`, `list_local`, plus `semanage_fcontext_validate_local`. The helper `validate_handler` checks each local context against a `sepol_policydb_t`.

Control flow: CRUD wrappers obtain `semanage_fcontext_dbase_local(handle)` and delegate to `dbase_*`. Validation iterates local records; if a record has a non-NULL context, it calls `sepol_context_check` against the policydb and reports the expression/type on failure.

State/persistence: local records persist through the local fcontext database configured in the handle. Validation does not write state; it is a pre-commit safety check.

Dependencies/integration: used by commit flows and by public fcontext APIs; relies on `handle.h` inline database selectors, `database.h`, and libsepol context validation. Risks include local records with NULL contexts being accepted and error reporting depending on successful context string conversion. Test signals include local modify/delete/query and commit rejection for invalid context types/users/roles.
