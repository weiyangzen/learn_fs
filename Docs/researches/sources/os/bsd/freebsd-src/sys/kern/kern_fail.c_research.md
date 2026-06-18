# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_fail.c

Read status: complete file reviewed.

This file implements the FreeBSD failpoint facility, allowing runtime fault injection through sysctl strings. It parses failpoint programs, installs them atomically, evaluates them cheaply when enabled, supports probabilistic/count/pid-qualified actions, reports state, and garbage-collects old settings after concurrent users drain.

Main public entry points include `fail_point_init`, `fail_point_destroy`, `fail_point_alloc_callout`, `fail_point_is_off`, `fail_point_eval_nontrivial`, `fail_point_sysctl`, `fail_point_sysctl_status`, and `fail_sysctl_drain_func`. The debug sysctl `debug.fail_point.test_trigger_fail_point` exercises the test failpoint.

The internal model uses `struct fail_point`, `struct fail_point_setting`, and `struct fail_point_entry`. A setting contains a queue of entries; each entry has a type, argument, probability in millionths, optional fire count, optional pid restriction, stale flag, and parent pointer. Settings are swapped via `fail_point_swap_settings`, while readers take references by incrementing `fp_ref_cnt` before reading `fp_setting`.

Supported action types are `off`, `panic`, `return`, `break`, `print`, `sleep`, `pause`, `yield`, and `delay`. Evaluation applies probability, pid, and count filters, then executes the first non-continuing matching action. `print` can request continuation using its argument. `sleep` can either block through `tsleep` or queue a timeout callout when `FAIL_POINT_USE_TIMEOUT_PATH` is set. `pause` sleeps until the failpoint is changed or disabled. Sleep actions in `FAIL_POINT_NONSLEEPABLE` contexts are converted to busy delays.

Sysctl setting is serialized by `sx_fp_set`. `fail_point_set` parses a new program into a fresh setting, removes impossible zero-probability or zero-count entries, truncates unreachable entries after permanent `off` or `pause`, wakes paused threads when needed, and swaps the setting into the failpoint. Old settings remain on a garbage list until no evaluator references exist. `fail_point_drain` is used during destroy to swap off the setting, wake paused waiters, wait for refs to drain, drain any callout, and restore or clean state.

The parser accepts chains of terms separated by `->`. Each term supports optional probability like `12.5%`, optional count like `3*`, a type name, optional integer argument in parentheses, and optional `[pid N]`. `parse_number` rounds fractional probabilities to the supported precision, and `FP_MAX_ENTRY_COUNT` bounds sysctl-provided chains.

Status output converts active entries back to text and can optionally include sleeping/paused thread counts and, with `STACK`, stack traces for sleepers. Sysctl output uses an sbuf drain callback to stream to the sysctl request.

Concurrency design depends on atomic refcounts, a spin mutex for the garbage list, and the sleepable sx lock for set/get operations. Old settings are not freed while any evaluator might still be walking them, and stale entries are ignored until collection.

Risk areas are refcount correctness in `fail_point_setting_get_ref/release_ref`, races between evaluator stale marking and sysctl replacement, pause/sleep wakeup semantics during destroy, parser acceptance of malformed chains, count decrement atomicity, and the distinction between sleepable and non-sleepable failpoints.
