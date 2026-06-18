# sources/object-store/rustfs/crates/audit/src/global.rs

## Purpose

`global.rs` provides the process-wide audit system facade. It lazily initializes a singleton `AuditSystem`, exposes lifecycle operations, dispatches audit entries when the system is running, reports target metrics, and offers the `AuditLogger` convenience type.

## Important APIs and Types

`init_audit_system` initializes a `OnceLock<Arc<AuditSystem>>`; `audit_system` reads it. `start_audit_system`, `stop_audit_system`, `pause_audit_system`, `resume_audit_system`, `reload_audit_config`, `audit_target_metrics`, and `is_audit_system_running` wrap the singleton. `dispatch_audit_log` accepts `Arc<AuditEntry>` and drops entries with structured logs when the system is uninitialized or not running. `AuditLogger::log`, `is_enabled`, and `instance` provide an ergonomic global logger facade.

## Control Flow

Lifecycle calls use the singleton when available; the `with_audit_system!` macro treats missing initialization as a logged no-op returning `Ok(())`. Starting is different: it always initializes then calls `AuditSystem::start(config)`. Dispatch first checks singleton presence, then asynchronously checks `system.is_running()`, then calls `system.dispatch(entry)` or logs a dropped event.

## State and Persistence

The only state here is the `OnceLock` singleton. Once initialized, it cannot be replaced in-process. Persistent target state and replay queues are owned by `AuditSystem` and lower layers. Dispatch accepts `Arc<AuditEntry>` to avoid unnecessary cloning at the global boundary.

## Dependencies and Integration Points

It integrates with `AuditSystem`, `AuditEntry`, RustFS server `Config`, target metric snapshots, and `tracing` structured logs. Public re-export from `lib.rs` makes this the easiest entry point for request/API code to start and use auditing.

## Risks and Edge Cases

Because `OnceLock` cannot be reset, tests and process lifecycle code must account for singleton persistence. Operations other than start silently succeed when uninitialized, which keeps callers simple but can hide missing initialization unless debug logs are monitored. Dispatch drops entries when paused/stopped rather than buffering at this layer. `AuditLogger::log` only logs dispatch errors; target-level partial failures may already have been converted to metrics/logs by the pipeline.

## Test Signals

Tests should cover start/stop/pause/resume/reload delegation, no-op behavior before initialization, dropped-entry logging when not running, `AuditLogger::is_enabled`, metrics empty vector before init, and singleton behavior across repeated `init_audit_system` calls.
