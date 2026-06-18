# sources/security-integrity/selinux/libsemanage/tests/utilities.c

## Purpose
`utilities.c` provides shared fixtures and helper functions for libsemanage CUnit suites. It creates a minimal direct policy store, writes binary or CIL policy fixtures, manages the global semanage handle, and wraps common connect/transaction/commit lifecycle steps.

## Important APIs, Types, and Functions
The file defines the global `semanage_handle_t *sh` and helper functions declared in `utilities.h`: `test_msg_handler`, `create_test_store`, `destroy_test_store`, `enable_test_store`, `disable_test_store`, `write_test_policy_from_file`, `write_test_policy_src`, `helper_handle_create`, `helper_handle_destroy`, `helper_connect`, `helper_disconnect`, `helper_begin_transaction`, `helper_commit`, `setup_handle`, `cleanup_handle`, and `setup_handle_invalid_store`.

Internal helper `write_test_policy` writes `policy.kern`. The file uses libsemanage APIs such as `semanage_set_root`, `semanage_handle_create`, `semanage_msg_set_callback`, `semanage_set_create_store`, `semanage_set_reload`, `semanage_set_store_root`, `semanage_select_store`, `semanage_connect`, `semanage_disconnect`, `semanage_begin_transaction`, and `semanage_commit`.

## Control Flow
`create_test_store` constructs `test-policy/store/active/modules` and `test-policy/etc/selinux`, creates an empty `semanage.conf`, and enables test-store mode. Policy-writing helpers write either `store/active/policy.kern` from a file buffer or `store/active/modules/100/base/cil` plus a `lang_ext` marker of `cil`.

`helper_handle_create` optionally points libsemanage at `test-policy`, creates a handle, installs a silent message callback, and, when the test store is enabled, configures direct access to the `"store"` policy store without reload. `setup_handle` advances through null, handle, connected, and transaction states based on `level_t`; `cleanup_handle` unwinds in reverse, committing transactions when needed.

## State and Persistence Behavior
The global `test_store_enabled` controls whether newly created handles target the local fixture store. `destroy_test_store` uses `fts_open`/`fts_read` to recursively remove `test-policy` and disables test-store mode first. `cleanup_handle(SH_TRANS)` commits by design, so tests that need rollback semantics cannot use it directly without custom cleanup.

## Dependencies and Integration Points
Dependencies include POSIX filesystem APIs, FTS traversal, CUnit assertions, and the libsemanage public API. This file is the central integration point for most libsemanage tests in this subset.

## Risks and Edge Cases
Many `mkdir` calls fail if directories already exist, so stale `test-policy` state can prevent suite setup. `write_test_policy_from_file` does not check the return value of `fread`. `destroy_test_store` continues after remove failures and returns `-1` if any deletion failed. `helper_handle_destroy` does not set `sh` to NULL; callers rely on `cleanup_handle` to do that at the end.

## Test Signals
This helper file is validated indirectly by every suite that can create the store, connect, begin transactions, commit, and cleanly remove `test-policy`. Failures surface as suite initialization errors or fatal CUnit assertions in helper calls.
