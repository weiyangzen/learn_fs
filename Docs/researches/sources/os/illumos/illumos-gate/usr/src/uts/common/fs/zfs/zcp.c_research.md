# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zcp.c

## Role
Implements the ZFS Channel Program runtime around an embedded modified Lua 5.2 interpreter. It compiles/evaluates channel-program scripts, exposes constrained ZFS libraries, converts between Lua tables and nvlists, enforces instruction/memory/cancel limits, manages cleanup handlers, and standardizes argument parsing.

## Runtime Configuration
- `zfs_lua_check_instrlimit_interval`: Lua hook interval, default 100 instructions.
- `zfs_lua_max_instrlimit`: maximum caller-provided instruction limit.
- `zfs_lua_max_memlimit`: maximum caller-provided memory limit.
- `ZCP_NVLIST_MAX_DEPTH`: max Lua table to nvlist nesting depth, 20.

## Lua/NVList Conversion
- `zcp_table_to_nvlist()` converts Lua tables to unique-key nvlists, explicitly detecting possible collisions between string keys and converted numeric/boolean keys.
- `zcp_lua_to_nvlist_impl()` accepts nil, boolean, number, string, and table values; unsupported types push an error.
- `zcp_convert_return_values()` wraps the conversion so conversion failures become channel-program errors.
- `zcp_nvlist_to_lua()` converts all-boolean nvlists to Lua string arrays; otherwise converts key/value nvlists to Lua tables.
- `zcp_nvpair_value_to_lua()` supports boolean_value, string, int64, nvlist, string_array, uint64_array, and int64_array values.

## Error, Cleanup, And Dataset Helpers
- `zcp_error_handler()` runs registered cleanup handlers and returns a Lua traceback.
- `zcp_register_cleanup()`, `zcp_deregister_cleanup()`, and `zcp_cleanup()` ensure kernel resources are freed if Lua longjmps through C callbacks.
- `zcp_argerror()` formats argument errors through Lua's argerror path.
- `zcp_dataset_hold_error()` maps dataset hold errors to user-facing Lua errors; `zcp_dataset_hold()` wraps `dsl_dataset_hold()`.

## Built-in Global Functions
- `zcp_debug()` writes a ZFS debug message tagged with the txg.
- `zcp_exists()` checks if a dataset exists in the target pool and returns a Lua boolean, with errors for cross-pool or I/O failures.
- `zcp_load_globals()` from `zcp_global.c` adds errno constants before loading ZFS modules.

## Memory And Instruction Limits
- `zcp_lua_alloc()` is the Lua allocator, tracking allocated bytes with a header word and enforcing `memlimit` once script execution begins.
- Shrinks return the same allocation because Lua requires shrink reallocations to succeed.
- `zcp_lua_counthook()` checks cancellation/signal state and instruction limit, raising Lua errors for cancellation or timeout.
- `zcp_panic_cb()` panics on unprotected Lua API errors.

## Evaluation Path
- `zcp_eval()` validates limits, creates a Lua state with custom allocator, opens selected base/coroutine/string/table libraries, loads globals, builds the `zfs` table with `list`, `check`, `sync`, `get_prop`, `debug`, and `exists`, compiles script text, converts input nvpair to Lua, and runs in sync or open context.
- Sync mode uses `dsl_sync_task_sig()` with `zcp_eval_sync()` and signal callback `zcp_eval_sig()`.
- Open/dry-run mode uses `zcp_eval_open()`, holds the pool, creates an abort-only transaction so check functions can run, evaluates, then aborts.
- `zcp_eval_impl()` installs run info in the Lua registry, enables count hook, switches allocator from must-succeed to limited mode, calls Lua, converts one return value or error into `outnvl`, and maps timeout/cancel/runtime/memory errors to errno.
- Multiple return values are rejected with `ECHRNG`.

## Argument Parsing
- `zcp_parse_args()` supports either positional arguments or a single table containing integer positional keys plus string keyword keys.
- `zcp_parse_table_args()` validates types, removes consumed entries, then rejects extra positional/keyword keys.
- `zcp_parse_pos_args()` validates fixed positional arity and appends nil placeholders for missing keyword values.
- `zcp_args_error()` builds structured function-signature messages while avoiding oversized error strings.

## Important Details
- ZCP changes are not automatically rolled back if a fatal Lua error occurs after earlier sync operations in the same channel program.
- `sync=FALSE` still lets check functions run in open context; actual `zfs.sync` mutations require sync evaluation.
- The runtime intentionally exposes only selected Lua libraries and ZFS-specific modules.
- Cleanup handlers are essential because many submodule functions allocate nvlists or crypto params before calling code that may longjmp.
