# File Research: sources/os/bsd/dragonflybsd/sys/kern/lwkt_token.c

## Scope

This file implements LWKT soft token locks. Tokens serialize running threads, but are released automatically when a thread blocks and reacquired by the scheduler when the thread resumes. The file also defines global subsystem tokens and a pool-token hash for type-stable per-object serialization.

## Public And Internal APIs Covered

- Global tokens: `mp_token`, `pmap_token`, `dev_token`, `vm_token`, `vmspace_token`, `kvm_token`, `sigio_token`, `tty_token`, `vnode_token`, `vga_token`, `kbd_token`.
- Boot and pool support: `cpu_get_initial_mplock()`, `lwkt_token_pool_init()`, `lwkt_token_pool_lookup()`, `lwkt_getpooltoken()`, `lwkt_relpooltoken()`.
- Token lifecycle and acquisition: `lwkt_token_init()`, `lwkt_token_uninit()`, `lwkt_gettoken()`, `lwkt_gettoken_shared()`, `lwkt_trytoken()`, `lwkt_reltoken()`, `lwkt_cnttoken()`, `lwkt_token_swap()`.
- Scheduler hooks: `lwkt_getalltokens()`, `lwkt_relalltokens()`, internal `_lwkt_getalltokens_sorted()`.
- Core internals: `_lwkt_token_pool_lookup()`, `_lwkt_tokref_init()`, `_lwkt_trytokref()`, `_lwkt_trytokref_spin()`, `_lwkt_reltokref()`.

## Control Flow And Behavior

- Tokens are represented by a shared count word plus an optional exclusive holder tokref. Shared holders increment by `TOK_INCR`; exclusive holders set `TOK_EXCLUSIVE`; contended blocking exclusive attempts can set `TOK_EXCLREQ`.
- `lwkt_gettoken()` pushes a tokref onto the current thread's token stack, tries to acquire exclusive ownership, and if it fails yields through `lwkt_switch()` with `td_toks_have` indicating the scheduler-owned reacquisition boundary.
- `lwkt_gettoken_shared()` follows the same model but acquires shared ownership. Debug builds warn about shared pool-token acquisition because unrelated objects can hash to the same token.
- Recursive exclusive acquisition by the same thread is allowed: the deeper reference owns `t_ref`; later recursive acquisitions are treated count-wise like shared refs for simpler release.
- `lwkt_trytoken()` sets up a temporary exclusive tokref, attempts nonblocking acquisition without setting `TOK_EXCLREQ`, and rolls back `td_toks_stop` on failure.
- `lwkt_reltoken()` enforces strict reverse-order release from the thread token stack and panics with diagnostic output if the token does not match the top ref.
- `_lwkt_trytokref_spin()` uses exponential backoff for exclusive contention and TSC windowing for shared contention before giving up to the scheduler.
- `lwkt_getalltokens()` is called by the scheduler when resuming a thread. It reacquires all tokrefs in forward order, or address-sorted order after enough contention, releasing partial acquisitions on failure.
- `_lwkt_getalltokens_sorted()` sorts tokrefs by token address while preserving recursive acquisition order for equal tokens, reducing deadlock risk during decontention.
- `lwkt_relalltokens()` releases all current thread tokens in reverse order when a thread switches away.
- Pool tokens hash arbitrary pointers into a 16,384-entry cache-aligned token pool using two prime-modulo hash components.
- `lwkt_token_swap()` swaps the top two tokrefs so callers can correct release order, while preserving `t_ref` identity for exclusive holders.

## State And Data Structures

- `struct lwkt_token` fields used include `t_count`, `t_ref`, `t_collisions`, and `t_desc`.
- `struct lwkt_tokref` records `tr_tok`, requested/held count bits in `tr_count`, and owning thread.
- Thread token stack spans `td_toks_base` through `td_toks_stop`, with `td_toks_have` used during scheduler reacquisition.
- Contention tuning is exposed through `lwkt.token_backoff_max`, `lwkt.token_window_shift`, per-token collision counters, and `tokens_debug_output`.

## Dependencies

- Depends on atomic compare/set and fetch-add operations, TSC reads, CPU pause/fence operations, LWKT scheduler switching, current-thread token stack state, and optional DDB/debug tracing.
- Closely coupled to `lwkt_thread.c`, which releases and reacquires tokens around context switches.

## Risks And Invariants

- Tokens must be released in exact reverse acquisition order unless `lwkt_token_swap()` is used deliberately.
- Blocking token acquisition is forbidden from hard interrupt/nesting contexts unless panic handling owns the CPU.
- Shared-to-exclusive upgrade while already holding only shared refs can livelock; debug builds assert this pattern.
- `t_ref` must be cleared before the exclusive bit is released and must continue to point at the deepest exclusive recursive ref.
- Scheduler token reacquisition is part of the deadlock-avoidance design; bypassing it would break the "released while blocked" token model.
