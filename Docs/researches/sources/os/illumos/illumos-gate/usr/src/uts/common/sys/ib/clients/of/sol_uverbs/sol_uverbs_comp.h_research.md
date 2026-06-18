# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_uverbs/sol_uverbs_comp.h

This sol_uverbs completion-queue header declares command handlers and event callback support for user CQ operations.

API surface:
- User command handlers for create, destroy, resize, request-notify, and poll CQ.
- `sol_uverbs_comp_event_handler()` handles IBTF CQ completion callbacks for a CQ.

Risk-sensitive invariants:
- CQ command handlers consume user ABI buffers with explicit input/output lengths.
- Completion delivery integrates with sol_uverbs event files and CQ event counters defined in `sol_uverbs.h`.
- CQ destruction must coordinate with active QPs and pending completion events.
