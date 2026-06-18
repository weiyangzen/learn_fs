# sources/object-store/daos/src/vos/vos_ilog.h

## Purpose
`vos_ilog.h` declares the VOS wrapper contract around generic incarnation logs. It defines conditional operation modes, punch records, parsed ilog state, tracing wrappers, timestamp-cache hooks, and failout policy for corrupted ilogs.

## Important APIs and Types
`enum` values `VOS_ILOG_COND_NONE`, `PUNCH`, `UPDATE`, `INSERT`, and `FETCH` describe conditional existence semantics. `ILOG_FLAGS_CORRUPTED` reserves ilog magic flag space for data-loss handling. `struct vos_punch_record` stores major and minor punch epochs. `struct vos_ilog_info` owns fetched `ilog_entries` plus parsed state for visible creation, committed and uncommitted punches, next punch, uncertainty, empty-log state, and full-range coverage. Public APIs mirror the implementation: fetch/init/move/finish, update, punch, check, set flags, aggregate, is-punched, descriptor callback setup, timestamp add/mark/evict/last-update, and `vos_ilog_failout`.

## Control Flow Contract
Callers initialize `vos_ilog_info`, fetch at an epoch with optional parent or external punch context, check visibility with `vos_ilog_check`, and finish the info object. Update and punch APIs perform a fetch internally before modifying the log so conditional checks and uncertainty handling are centralized. When `ILOG_TRACE` is enabled, macro wrappers preserve the API shape while logging inputs, outputs, parsed creation and punch fields, and returned epoch ranges.

## State and Persistence
The header does not define the durable ilog layout itself; that is `struct ilog_df` from `ilog.h`. It defines VOS interpretation of that durable state. `vos_ilog_info` is transient and must not be copied wholesale unless the entry list ownership is handled; `vos_ilog_copy_info` intentionally copies only parsed fields after `ii_entries`. The timestamp functions associate ilog roots with VOS read/write timestamp entries for conflict detection and cache eviction.

## Dependencies and Integration
The header includes DAOS common definitions, generic `ilog`, and `vos_ts`. It forward-declares `struct vos_container` so object and IO code can use ilog APIs without needing implementation details. `vos_internal.h` includes this header and supplies key helpers such as `vos_epc_punched` and DTX state. `vos_io.c` and object iterator code rely on `struct vos_ilog_info` to carry parent visibility down object, dkey, and akey levels.

## Risks and Test Signals
API risks include confusing `visible_only` versus punched visibility in `vos_ilog_check`, copying `ii_entries` incorrectly, and bypassing corrupted-log failout for normal intents. Tests should verify all conditional modes, the tracing macros under compile-time enablement, timestamp add/mark/evict behavior for valid and null timestamp sets, and that corrupted ilogs are accessible only for the explicit maintenance intents named in `vos_ilog_failout`.
