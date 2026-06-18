# sources/storage-engines/tikv/scripts/check-log-style

## Purpose
Enforces snake_case structured log keys in Rust code by rejecting quoted keys containing spaces or hyphens before `=>`.

## Important Commands and Control Flow
The script recursively greps `*.rs` files outside `target` with an extended regex, then filters out known allowed paths such as `config.rs`, `tikv_util/src/logger`, and `file_system/src/rate_limiter.rs`. Any remaining match prints `Prefer snake_case for log kv.` and exits 1; otherwise it prints `Log style check passed.`

## State, Dependencies, Integration
The script is read-only and depends on bash and grep. It integrates with TiKV's structured logging conventions and CI lint checks.

## Risks and Test Signals
Regex linting can miss complex macro forms or flag harmless strings. The exclusion list must be maintained with logging infrastructure. A Rust log field like `"bad-key" => value` should fail while `good_key => value` style should pass.
