# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zcp.h

This header declares ZFS Channel Program infrastructure, which evaluates Lua programs against pool/dataset state with resource limits and optional sync-task execution.

Core definitions:
- `ZCP_RUN_INFO_KEY` names the Lua registry/run-info key.
- Global limits `zfs_lua_max_instrlimit` and `zfs_lua_max_memlimit`.
- `zcp_cleanup_handler_t` stores cleanup function, argument, and list node for fatal-error cleanup.
- `zcp_alloc_arg_t` tracks Lua allocator must-succeed mode, remaining allocation budget, and limit.
- `zcp_run_info_t` stores DSL pool, estimated sync-task space used, invoking credentials, DMU transaction, instruction counters/limit, timeout/cancel/sync flags, cleanup handler list, Lua state, allocator args, output nvlist, and result errno.
- `zcp_arg_t` and `zcp_lib_info_t` describe positional/keyword argument specifications for Lua-exposed library functions.

Public API surface:
- Argument error helper, `zcp_eval()`, list library loader, sync-task library loader.
- Run-info lookup, cleanup registration/deregistration, cleanup execution.
- Argument parsing, nvlist-to-Lua conversion, dataset hold error reporting, and dataset hold helper.

Risk-sensitive invariants:
- Channel programs run with explicit instruction and memory limits; timeout/cancel state is part of run info.
- Sync channel programs must use original caller credentials for permission checks, not the synctask thread's current credentials.
- Cleanup handlers protect resources when Lua raises fatal errors.
