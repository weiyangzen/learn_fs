# sources/user-network-fs/nfs-ganesha/src/Protocols/RQUOTA/rquota_getquota.c

Purpose: implements RQUOTA GETQUOTA and extended GETQUOTA by resolving an export and reading FSAL quota state.

Important APIs/types/functions: exports `rquota_getquota` and `rquota_getquota_Free`; uses `check_handle_lead_slash`, export lookups by tag/pseudo/path, `set_op_context_export`, `nfs_req_creds`, and FSAL `get_quota`.

Control flow: it selects quota type/id from classic or extended version arguments, initializes status to `Q_EPERM`, normalizes the path, finds the matching export using tag/pseudo/path policy, installs the export into `op_ctx`, obtains request credentials, calls `get_quota`, maps no-quota to `Q_NOQUOTA`, and on success scales block counts/limits down until they fit 32-bit RQUOTA fields while increasing block size.

State and persistence: reads persistent FSAL quota accounting but does not modify it. It updates request context with an export reference that is expected to be released by normal request cleanup.

Dependencies and integration points: bridges RQUOTA wire structures, export manager, credentials, and FSAL quota APIs. It relies on `os/quota.h` for `USRQUOTA`.

Risks and test signals: export resolution policy, credential failure, scaling overflow, and result defaults are important. Test absolute/pseudo/tag paths, extended group/project quota types if supported, no quota, large 64-bit quota values, credential denial, and missing export.
