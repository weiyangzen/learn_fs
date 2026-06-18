# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/callb.c

## Purpose

`callb.c` implements the generic kernel callback table used for checkpoint/resume, debugger, and daemon coordination events. Callbacks are grouped by class and executed serially per class.

## Main Interfaces

Registration and deletion: `callb_init`, `callb_add`, `callb_add_thread`, `callb_delete`.

Execution/control: `callb_execute_class`, `callb_lock_table`, `callb_unlock_table`.

CPR helpers: `callb_generic_cpr`, `callb_generic_cpr_safe`, `callb_is_stopped`.

## Behavior

Callbacks are stored in `callb_table_t`, with class heads in `ct_first_cb[]`, a freelist, a table lock, and a busy gate preventing additions while callers lock the table.

`callb_add_common()` waits while the table is busy, allocates or reuses a callback record, records the target thread, function, argument, class, and name, then inserts at the class-list head.

`callb_delete()` locates the entry in its class, waits if the callback is executing, unlinks it, marks it free, and returns it to the freelist.

`callb_execute_class()` walks a class list under the table lock, marks each callback executing, drops the lock while calling it, and stops on the first callback failure, returning that callback name.

`callb_generic_cpr()` implements standard CPR daemon behavior by setting `CALLB_CPR_START`, optionally waiting until safe, and signaling resume. `callb_is_stopped()` checks whether a kernel thread is registered and safe/stopped for CPR, falling back to a symbol name for unknown threads.

## Notable Invariants

- `ct_lock` protects callback state and list membership.
- Deletion waits for `CALLB_EXECUTING` to clear.
- Execution drops the table lock around callback invocation.
- Callback names are bounded by `CB_MAXNAME`.
- The table busy flag prevents concurrent additions in special phases.

## Dependencies

Depends on kernel threads, condition variables, CPR protocol structures, task/thread state, `kobj_getsymname()`, and delay/retry constants.

## Research Notes

Key risks are callback deletion while class execution is walking the list, callbacks that block or recursively manipulate callback state, and CPR stop checks that depend on thread sleep/stop timing.
