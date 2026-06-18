# sources/object-store/openstack-swift/swift/common/daemon.py

## Purpose
`daemon.py` defines Swift's base daemon abstraction, the strategy for running a daemon inline or as multiple forked workers, and `run_daemon()` for loading config, preparing process environment, and starting daemon classes. It separates daemon business logic from process-management mechanics.

## Important APIs, types, and functions
- `Daemon` provides `run_once()`, `run_forever()`, `run(once=False)`, `post_multiprocess_run()`, `get_worker_args()`, and `is_healthy()` extension points.
- `DaemonStrategy` handles setup, signal behavior, inline execution, forking, worker tracking, worker restart, health-triggered worker replacement, and cleanup.
- `DaemonStrategy.setup()` validates config, drops privileges, cleans daemon hygiene, captures stdio, installs a SIGTERM handler that kills the process group, and sends systemd readiness notification.
- `run_daemon(klass, conf_file, section_name='', once=False, **kwargs)` derives the config section, reads config, monkey-patches eventlet, configures the hub/logger/priority/fallocate/debug/TZ environment, creates the daemon, and runs it through `DaemonStrategy`.

## Control flow
Subclasses implement `run_once()` and `run_forever()`. If a subclass returns no worker argument dictionaries from `get_worker_args()`, `DaemonStrategy` runs the daemon inline. If worker args are returned, it forks one process per option set, resets SIGHUP/SIGTERM and `NOTIFY_SOCKET` in children, and calls `daemon.run(once, **kwargs)`. The parent periodically asks whether the daemon is healthy, cleans up and respawns workers if not, reaps exited workers, respawns them in forever mode, and exits once all once-mode workers finish.

`run_daemon()` turns class names such as `ObjectReplicator` into section names such as `object-replicator` when none is supplied. It uses command-line `once` or `daemonize=false` to select once mode, configures logging and process priority, supports disabling fallocate, sets eventlet hub exception reporting, pins timezone to UTC, logs start/exit, and returns the daemon instance.

## State and persistence behavior
The strategy tracks worker PIDs and their option dictionaries in memory. It mutates process-level state: user privileges, stdio, signal handlers, process group behavior, eventlet monkey patching/hub selection, priority, fallocate settings, environment variables, and systemd notifications. It does not persist files directly.

## Dependencies and integration points
The module depends on Swift utilities for config reading, logging, privilege dropping, stdio capture, monkey patching, hub selection, priority, fallocate configuration, and systemd notifications. All long-running Swift service daemons can use `run_daemon()` as their entrypoint and inherit `Daemon` for run-once/run-forever behavior.

## Risks and edge cases
The SIGTERM handler sends SIGTERM to process group 0 and exits with `os._exit(0)`, so embedding this strategy in a larger process group would be dangerous. Forked children call `os._exit(0)` to avoid parent cleanup stacks, which is intentional but unforgiving. `register_worker_exit()` appends options for respawn even during cleanup; cleanup then leaves options in `unspawned_worker_options`, which is acceptable because the strategy is stopping. Health checks happen every five seconds by default, so worker option changes are not instantaneous. Eventlet monkey patching occurs inside `run_daemon()` and affects the whole process.

## Test signals
Tests should cover section-name derivation, config read errors, once versus daemonize selection, inline fallback, multi-worker fork/reap/respawn behavior, health-triggered cleanup, SIGTERM handling, child environment reset, systemd notifications, priority/fallocate/eventlet-debug configuration, and `post_multiprocess_run()` invocation after worker completion.
