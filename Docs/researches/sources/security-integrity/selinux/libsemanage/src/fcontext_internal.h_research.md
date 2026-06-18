# sources/security-integrity/selinux/libsemanage/src/fcontext_internal.h

Purpose: declares the internal file-context record hooks that connect the public `semanage_fcontext_*` APIs to libsemanage's generic database layer. It includes public fcontext local/policy headers, `sepol/policydb.h`, and the internal database/handle definitions.

Important APIs/types/functions: exports `SEMANAGE_FCONTEXT_RTABLE`, `fcontext_file_dbase_init`, `fcontext_file_dbase_release`, and `semanage_fcontext_validate_local`. The record table is implemented in `fcontext_record.c`; the file backend is implemented in `fcontexts_file.c`; local validation lives in `fcontexts_local.c`.

Control flow and integration: backend setup code calls `fcontext_file_dbase_init` to bind read-only/read-write file paths to the fcontext record table and file parser/printer. Commit validation can call `semanage_fcontext_validate_local` with a `sepol_policydb_t` to ensure locally configured contexts are policy-valid before flush.

State/persistence: this header owns no state; it defines the ABI between record, text-file, local, and policy database implementations. Risks are signature drift against implementation files and using the local validator without a loaded policydb. Test signals are compile coverage and fcontext modify/query/list/commit tests that exercise parser, record table, and validation.
