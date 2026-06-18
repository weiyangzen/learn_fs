<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/telemetry/mod.rs -->
# sources/object-store/rustfs/crates/obs/src/telemetry/mod.rs

Purpose: Provides the single entry point for RustFS telemetry initialization and the module boundary for observability backends. It decides between full OTLP export, local rolling-file logging, and stdout-only logging from an `OtelConfig`, then returns an `OtelGuard` that owns the provider/writer lifecycle.

Important APIs/types/functions: Re-exports `OtelGuard` and `Recorder`, exposes public `dial9`, and keeps `filter`, `guard`, `local`, `otel`, `recorder`, `resource`, and `rolling` private. `init_telemetry(config)` computes the effective environment and log level, detects whether any root or per-signal OTLP endpoint is configured, and delegates either to `otel::init_observability_http` or `local::init_local_logging`.

Control flow: `init_telemetry` first treats any non-empty OTLP endpoint (`endpoint`, `trace_endpoint`, `metric_endpoint`, or `log_endpoint`) as a request for the OTLP HTTP pipeline. If no OTLP endpoint exists, it checks `RUSTFS_OBS_LOG_DIRECTORY` dynamically and overlays it onto a cloned config so late environment changes still select file logging. Otherwise local logging chooses between file and stdout internally.

State/persistence behavior: This file does not persist telemetry data itself, but it controls which backend owns external state. Returning and retaining `OtelGuard` is mandatory because dropping it flushes and shuts down providers/writers. The only local mutation is constructing an effective config when the log-directory environment variable overrides the passed struct.

Dependencies/integration: Integrates `OtelConfig`, `TelemetryError`, RustFS config defaults (`DEFAULT_LOG_LEVEL`, `ENVIRONMENT`, production environment name, `ENV_OBS_LOG_DIRECTORY`), and `rustfs_utils::get_env_opt_str`. It is the integration seam callers should use instead of calling backend modules directly.

Risks/test signals: Endpoint detection treats any per-signal endpoint as full OTLP mode, so misconfigured single-signal settings can change logging/metrics behavior. The environment variable override is intentionally dynamic but can surprise code that expects the provided config to be authoritative. Unit tests cover production detection, stdout default logic, log-level mapping expectations, and environment field defaults; they do not instantiate real subscribers or exercise `init_telemetry` end to end.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/telemetry/mod.rs -->
