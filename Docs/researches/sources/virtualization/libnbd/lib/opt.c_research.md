# File Research: sources/virtualization/libnbd/lib/opt.c

Implements option-negotiation mode APIs, both synchronous and asynchronous.

Key functions:
- `nbd_internal_free_option`: frees option callbacks according to current option type.
- `nbd_unlocked_set_opt_mode` / `get_opt_mode`: configure option mode.
- `wait_for_option`: polls while connecting.
- Synchronous option APIs for GO, INFO, ABORT, STARTTLS, EXTENDED_HEADERS, STRUCTURED_REPLY, LIST, LIST_META_CONTEXT, SET_META_CONTEXT.
- Async option APIs set `h->opt_current`, store callbacks, transfer callback ownership, and kick the generated state machine with `cmd_issue`.
- Metadata context query helpers copy explicit queries or use the handle’s requested contexts.

Interactions:
- Generated state machine consumes `h->opt_current`, `h->opt_cb`, and `h->querylist`.
- `utils.c` supplies query-list copying.
- `flags.c`/state-machine code stores negotiated export and metadata results.

Research notes:
- Synchronous wrappers are thin async wrappers plus polling and completion-error interpretation.
- Fixed-newstyle is required for most options beyond GO/ABORT.
- STARTTLS is compile-time gated on GnuTLS.
