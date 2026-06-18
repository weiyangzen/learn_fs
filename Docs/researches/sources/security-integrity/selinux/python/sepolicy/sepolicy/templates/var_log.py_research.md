# sources/security-integrity/selinux/python/sepolicy/sepolicy/templates/var_log.py
# sources/security-integrity/selinux/python/sepolicy/sepolicy/templates/var_log.py

Purpose: template fragments for application log files.

Important APIs and control flow: declares `TEMPLATETYPE_log_t` with `logging_log_file`, grants manage access and `logging_log_filetrans`, defines interfaces for read, append, and manage log files plus admin additions, and emits file/directory contexts.

State and persistence: rendered policy controls durable log labels and access.

Dependencies and integration points: depends on reference-policy logging macros such as `logging_search_logs`, `logging_log_file`, and `logging_log_filetrans`.

Risks and test signals: manage-log permissions include deletion and rewrite; append-only access is safer for non-admin consumers. No direct tests cover generated logging policy.
