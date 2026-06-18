# sources/user-network-fs/samba/source3/utils/net_rpc_audit.c

## Purpose

`net_rpc_audit.c` implements the `net rpc audit` command family. It lets the Samba `net` utility view and modify a target server's global LSA auditing configuration through MSRPC. The supported subcommands are `list`, `get <category>`, `set <category> <policy>`, `enable`, and `disable`.

The file does not create connections itself. Public wrappers call `run_rpc_command()` with `ndr_table_lsarpc`, then the internal callbacks operate on the supplied LSA RPC pipe.

## Important APIs, Types, and Functions

`net_help_audit()` prints the command help and accepted category/policy names. `print_auditing_category()` formats one audit category row and substitutes fallback labels for NULL policy/value strings.

`rpc_audit_get_internal()` validates a category with `get_audit_category_from_param()`, opens LSA policy, queries `LSA_POLICY_INFO_AUDIT_EVENTS`, and prints the selected setting using `audit_policy_str()` and `audit_description_str()`.

`rpc_audit_set_internal()` validates category and policy, maps `Success`, `Failure`, `All`, or `None` to `LSA_AUDIT_POLICY_*` bits, queries the current audit-events policy, updates `settings[audit_category]`, writes it back with `dcerpc_lsa_SetInfoPolicy()`, re-queries, and prints the resulting setting.

`rpc_audit_enable_internal_ext()` is the shared implementation for global auditing mode changes. It queries `LSA_POLICY_INFO_AUDIT_EVENTS`, sets `info->audit_events.auditing_mode`, and writes the policy back. `rpc_audit_enable_internal()` and `rpc_audit_disable_internal()` call it with `true` or `false`.

`rpc_audit_list_internal()` opens LSA policy, queries audit events, prints enabled/disabled state, prints category count, and prints every category setting.

The command wrappers `rpc_audit_get()`, `rpc_audit_set()`, `rpc_audit_enable()`, `rpc_audit_disable()`, and `rpc_audit_list()` handle usage output and delegate through `run_rpc_command()`. `net_rpc_audit()` registers the subcommands with `net_run_function()`.

## Control Flow

`net_rpc()` dispatches `audit` to `net_rpc_audit()`. `net_rpc_audit()` selects the subcommand. Each wrapper either prints usage or calls `run_rpc_command(c, NULL, &ndr_table_lsarpc, 0, callback, argc, argv)`. The callback opens an LSA policy handle, queries or mutates `LSA_POLICY_INFO_AUDIT_EVENTS`, reports errors, and returns NTSTATUS.

`get` and `set` operate on one category. `enable` and `disable` modify only the global `auditing_mode`. `list` is read-only and prints the global mode plus every category.

## State and Persistence Behavior

`get` and `list` are read-only. `set` changes one element of `info->audit_events.settings[]` and writes the full audit-events policy back. `enable` and `disable` change `info->audit_events.auditing_mode` and also write the full policy back. No local files are persisted.

Memory is owned by the `mem_ctx` from `run_rpc_command()`. The file opens LSA policy handles but does not explicitly close them, relying on command/pipe teardown.

## Dependencies and Integration Points

The file includes `utils/net.h`, `rpc_client/rpc_client.h`, generated `ndr_lsa_c.h`, and `rpc_client/cli_lsarpc.h`. It depends on `run_rpc_command()` and audit helper functions declared outside this file. It integrates into the top-level `net rpc` table through `net_rpc_audit()` and uses Samba localization wrappers for output.

## Risks and Edge Cases

`get` accepts one or two arguments but ignores the second; `set` accepts two or three and ignores the third. The help text shows uppercase policies, while implementation compares title-case strings (`Success`, `Failure`, `All`, `None`), so behavior depends on `strequal()` being case-insensitive. The code trusts `get_audit_category_from_param()` to return an in-range index for `settings[]`.

Because `set`, `enable`, and `disable` query an entire policy object, modify one field, and write the object back, concurrent administrative changes can be overwritten. All operations request maximum allowed policy access, and policy handles are not explicitly closed.

## Test Signals

Useful tests include dispatch and usage tests for every subcommand, argument validation for missing/invalid/extra arguments, case-sensitivity tests for documented uppercase policies, integration tests that `list` prints all categories, tests that `set` persists one category and `enable`/`disable` preserve category settings, permission-denied tests, and static checks for category bounds and explicit policy handle cleanup.
