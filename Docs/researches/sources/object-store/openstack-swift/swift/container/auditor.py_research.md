# sources/object-store/openstack-swift/swift/container/auditor.py

## Purpose
This module defines the container auditor daemon entrypoint. It specializes Swift's generic `DatabaseAuditor` for container databases by selecting `ContainerBroker` and the `container` server type.

## Important APIs, Types, and Functions
- `ContainerAuditor(DatabaseAuditor)` sets `server_type = "container"` and `broker_class = ContainerBroker`.
- `ContainerAuditor._audit(job, broker)` currently returns `None`, meaning container-specific extra audit checks are not implemented here beyond the generic database auditor behavior.
- `main()` parses daemon options with `parse_options(once=True)` and runs the daemon through `run_daemon(ContainerAuditor, conf_file, **options)`.

## Control Flow and Behavior
CLI execution calls `main()`, which delegates option parsing and daemon lifecycle to shared Swift helpers. During audit runs, the inherited `DatabaseAuditor` opens container DBs through `ContainerBroker`; this subclass does not add per-container validation in `_audit()`.

## State and Persistence
State and persistence are inherited from `DatabaseAuditor` and `ContainerBroker`; this file itself stores no state. The audited persistence target is the SQLite-backed container database tree.

## Dependencies and Integration Points
It depends on `swift.container.backend.ContainerBroker`, `swift.common.daemon.run_daemon`, `swift.common.db_auditor.DatabaseAuditor`, and `swift.common.utils.parse_options`. It integrates with Swift daemon management and config files for container auditor processes.

## Risks and Edge Cases
- The no-op `_audit()` means corruption or invariant checks must come from the generic database auditor; container-specific shard and policy invariants are not checked here.
- Any change to `broker_class` affects which database layout the auditor can inspect.

## Test Signals
Tests should verify daemon option parsing, subclass attributes, that `run_daemon()` is called with `ContainerAuditor`, and that inherited auditor flows instantiate `ContainerBroker` for container database paths.
