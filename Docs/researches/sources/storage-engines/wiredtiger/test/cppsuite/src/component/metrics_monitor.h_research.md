# sources/storage-engines/wiredtiger/test/cppsuite/src/component/metrics_monitor.h

Purpose: Declares the metrics-monitor component and stat cursor helper.

Important APIs/types/functions: `metrics_monitor` inherits `component`, exposes static `get_stat`, overrides `load`, `do_work`, and `finish`, and stores test name, database reference, session, cursor, and stat-checker list.

Control flow: standard component lifecycle with runtime checks during `do_work` and final checks in `finish`.

State and persistence: keeps active WiredTiger session/cursor state while running; may persist metrics through `metrics_writer`.

Dependencies/integration: includes configuration, database, scoped session/cursor, and statistics interfaces.

Risks and test signals: lifetime of `_database` must outlive the monitor. Statistics cursor availability depends on connection configuration enabling statistics where needed.
