# sources/security-integrity/cryfs/crates/tempproject/src/project.rs

Purpose: implements build and run operations for temporary Cargo projects and reports process failures with captured output.

Important APIs/types/functions: `ProcessError` stores exit code plus UTF-8 conversion results for stdout/stderr. `TempProject` owns the `TempDir` and separate `OnceLock<Result<PathBuf, ProcessError>>` slots for debug/release executables. `build_debug`, `build_release`, `run_debug`, and `run_release` are the main APIs. `find_single_binary_in()` locates exactly one executable file under the target profile directory.

Control flow: `_build_debug/_build_release` run `env!("CARGO") build` with an explicit temp `target` directory, inspect `assert_cmd` output, and either locate an executable or build `ProcessError`. `run_*` uses `get_or_init` to reuse a cached build result and returns an `assert_cmd::Command` in the project directory.

State/persistence: writes Cargo build artifacts under the temp project's `target` directory. The temp directory persists while `TempProject` is alive. `run_*` caches build results; `build_*` currently computes a fresh result and then ignores `OnceLock::set` failure, so repeated direct build calls may rebuild.

Dependencies/integration: depends on `assert_cmd`, `is_executable`, `tempfile`, `thiserror`, and standard path/process output handling. Used by tests that need a compiled binary path or command assertion object.

Risks: panics if Cargo produces zero or multiple executable files. `env!("CARGO")` is compile-time environment dependent. UTF-8 conversion errors are stored, not rendered as bytes. Direct `build_*` cache behavior differs from documentation.

Test signals: `tests/simple.rs` covers debug/release build success, build failure, runtime failure, and build-then-run combinations.
