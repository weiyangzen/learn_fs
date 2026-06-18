<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/lsm.c -->
# sources/test-tools/strace/src/lsm.c

Purpose: decodes Linux Security Module self-attribute and module-list syscalls.
Important APIs/types/functions: `lsm_get_self_attr`, `lsm_set_self_attr`, `lsm_list_modules`, `decode_lsm_ctx_sequence`, `struct lsm_ctx`, `lsm_attrs`, `lsm_flags`, and `lsm_ids`.
Control flow: get/list syscalls save entry-side sizes in `tcb` private data, then decode exit buffers and print changed sizes; set decodes a single context on entry. Sequence decoding walks variable-length `lsm_ctx` records with truncation protection.
State and persistence behavior: per-syscall saved size only. Dependencies and integration points: new Linux LSM syscall table entries.
Risks: variable-length records can be malformed; size-change reporting must match kernel behavior. Test signals: single and multi-context buffers, changed sizes, truncation, failed syscalls, and unknown ids.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/lsm.c -->
