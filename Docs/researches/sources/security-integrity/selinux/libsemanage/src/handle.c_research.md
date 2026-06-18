# sources/security-integrity/selinux/libsemanage/src/handle.c

Purpose: implements the public handle lifecycle and connection/transaction controls for libsemanage. It creates handles, parses configuration, owns the libsepol handle, selects stores, and dispatches backend operations through `semanage_policy_table`.

Important APIs/functions: `semanage_set_root`, `semanage_root`, `semanage_handle_create_with_path`, `semanage_handle_create`, setters for rebuild/reload/checks/store behavior, `semanage_get_hll_compiler_path`, dontaudit/tunable/cache settings, default priority accessors, `semanage_select_store`, `semanage_set_store_root`, `semanage_is_managed`, `semanage_mls_enabled`, `semanage_connect`, `semanage_access_check`, `semanage_disconnect`, `semanage_handle_destroy`, `semanage_begin_transaction`, and `semanage_commit`.

Control flow: handle creation allocates zeroed state, parses config, creates a sepol handle, installs the message relay, sets defaults such as priority 400, reload behavior based on SELinux status, file-context checks enabled, and commit lock timeout. Connection currently supports direct stores and delegates to direct backend functions. Transactions require a connected handle; commit delegates to backend commit and clears transaction/module flags afterward.

State/persistence: handle state includes connection flags, transaction flags, module modification flag, policy options, config, sepol handle, backend function table, and database slots. `private_semanage_root` is process-global. Persistent policy changes occur through backend commit, not directly here.

Risks: several setters assert allocation success and cannot return allocation errors; unsupported connection types fail at runtime; global root is not thread-local. Test signals include create/destroy, direct connect/disconnect, transaction idempotence, priority validation, compiler path lowercasing, and commit rejection without a transaction.
