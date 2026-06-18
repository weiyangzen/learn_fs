# File Research: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt.c

Implements the generic asynchronous FTL management process engine.

Key model:
- A process descriptor supplies named steps, optional per-process context, init/deinit handlers, and error handler.
- Each step has action, optional cleanup, timing/status fields, and optional step context.
- Actions run on the FTL core thread; final completion is posted back to the caller thread.
- Completed action steps with cleanup are pushed onto rollback todo in reverse order.
- `ftl_mngt_fail_step` marks failure, records the current step as failed, switches to rollback, and executes cleanup steps.

Important APIs:
- `ftl_mngt_process_execute`
- `ftl_mngt_process_rollback`
- context accessors
- `ftl_mngt_next_step`, `skip_step`, `continue_step`, `fail_step`
- child process invocation and rollback invocation

Role: all startup, shutdown, restore, scrub, metadata, property, and recovery flows are assembled as deterministic step machines over this engine.
