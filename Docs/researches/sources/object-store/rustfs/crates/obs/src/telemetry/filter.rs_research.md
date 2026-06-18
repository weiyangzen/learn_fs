# sources/object-store/rustfs/crates/obs/src/telemetry/filter.rs

## Purpose
Builds `tracing_subscriber::EnvFilter` instances for local, file, and OTLP logging while suppressing noisy dependencies under non-verbose configurations.

## Important APIs, Types, and Functions
Private helpers include `is_verbose_level`, `is_level_token`, `rust_log_requests_verbose`, `should_suppress_noisy_crates`, `directive_applies_to_target`, `effective_level_for_target`, and `should_demote_http_request_logs`. The exported crate-internal `build_env_filter(logger_level, default_level)` chooses the base directive from `default_level`, `RUST_LOG`, or `logger_level`, then appends `off` directives for `hyper`, `tonic`, `h2`, `reqwest`, and `tower` when appropriate. It may demote `rustfs::server::http` to WARN for info/warn defaults.

## Control Flow
The key branch is precedence: forced `default_level` wins, then `RUST_LOG`, then configured logger level. Suppression is skipped if the effective configuration requests debug/trace or target-only verbose directives. Target effective level resolution chooses the most specific and latest matching directive.

## State and Persistence
No persisted state. Reads process environment variable `RUST_LOG` at filter construction time.

## Dependencies and Integration Points
Used by `telemetry/local.rs` and likely other telemetry setup modules to keep log filtering consistent. Depends on `tracing_subscriber::EnvFilter` and `LevelFilter`.

## Risks
EnvFilter directive precedence is subtle. Appending suppressions can override broad directives, so helper logic must correctly detect explicit verbose intent. HTTP log demotion deliberately avoids falling back to `logger_level` when `RUST_LOG` only sets unrelated targets.

## Test Signals
The file has extensive unit tests for verbosity detection, `RUST_LOG` parsing, suppression decisions, HTTP demotion, injected suppressions, verbose `RUST_LOG` preservation, RUST_LOG precedence, target-only directives, and avoiding accidental HTTP log promotion.
