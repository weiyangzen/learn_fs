# sources/object-store/garage/src/garage/cli/remote/worker.rs

Purpose: implements remote CLI worker inspection and runtime background-variable get/set controls.

Important APIs/types/functions: `Cli::cmd_worker`, `cmd_list_workers`, `cmd_worker_info`, `cmd_get_var`, `cmd_set_var`, and `format_worker_state`.

Control flow: list fetches local workers with busy/error filters, sorts busy/throttled first, and prints state/progress/queue/error fields. Info fetches one worker and prints state, tranquility, errors, progress, queue length, persistent errors, and freeform messages. Get/set variable commands target selected node or all nodes and print per-node results/errors.

State and persistence: worker variable set can mutate runtime and persisted background settings depending on server-side variable registration, such as resync/scrub tranquility and worker count. List/info are read-only.

Dependencies and integration points: uses admin worker API types, `format_table`, `timeago`, shared local/multi API wrappers, and worker status response shape from background runner.

Risks: variable names/values are stringly typed and validated server-side. All-node set can partially succeed; errors are printed to stderr but the command returns `Ok(())`, so automation must parse output if partial failure matters.

Test signals: no direct tests; background/admin API tests and manual CLI runs should cover list/info and variable mutation.
