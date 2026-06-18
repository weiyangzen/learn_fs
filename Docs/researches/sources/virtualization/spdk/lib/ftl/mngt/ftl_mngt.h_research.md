# File Research: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt.h

Public interface for the FTL management process framework.

Defines callback types:
- `ftl_mngt_fn`
- `ftl_mngt_init_fn`
- `ftl_mngt_completion`

Defines descriptors:
- `ftl_mngt_step_desc`: name, optional context size, action, optional cleanup.
- `ftl_mngt_process_desc`: name, process context size, error/init/deinit handlers, and flexible step array.

Exports process execution/rollback, context accessors, finish/next/skip/continue/fail controls, nested process calls, and top-level management entry points for startup, trim, and shutdown.

Design note: callbacks are explicitly step-only APIs; the engine owns sequencing, rollback ordering, and caller completion.
