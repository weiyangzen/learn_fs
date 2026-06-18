# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/fptr_wlist.h

Header for Unbound's function-pointer whitelist checks. It documents the security goal: before indirect callback invocation, ensure callback pointers match known legitimate functions to reduce exploitability of overwritten function pointers.

Key contents:
- Defines `fptr_ok(x)`, which calls `fatal_exit(...)` on whitelist failure unless `EXPORT_ALL_SYMBOLS` disables it for Windows DLL/exe layouts.
- Declares whitelist checkers for:
  - network callbacks: `comm_point`, raw `comm_point`, timers, signals, accept/stop-accept callbacks, libevent-style callbacks;
  - pending UDP/TCP and serviced-query callbacks;
  - red-black tree comparators and LRU hash callbacks;
  - module environment service callbacks: `send_query`, `attach_sub`, `detach_subs`, `add_sub`, `kill_sub`, `detect_cycle`;
  - module lifecycle and state-machine callbacks: `init`, `deinit`, `startup`, `destartup`, `operate`, `inform_super`, `clear`, `get_mem`;
  - allocation cleanup, tube listen handlers, mesh callbacks, config print callbacks, inplace EDNS/reply/query callbacks, and serve-expired lookup callbacks.
- Includes declarations for test helper comparators (`order_lock_cmp`, `codeline_cmp`, `replay_var_compare`) because the whitelist implementation needs to recognize them.

Dependencies:
- Pulls in callback type definitions from `util/netevent.h`, `util/storage/lruhash.h`, `util/module.h`, `util/tube.h`, and `services/mesh.h`.
- Relies on `fatal_exit` from logging infrastructure.

Research notes:
- This header is an API/security boundary rather than an implementation file; actual whitelist membership lives in `util/fptr_wlist.c`.
- `mini_ev_cmp` from `mini_event.c` is one known consumer-side comparator that is whitelisted in the implementation.
