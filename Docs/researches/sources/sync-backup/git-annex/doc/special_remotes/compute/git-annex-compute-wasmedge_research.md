<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/doc/special_remotes/compute/git-annex-compute-wasmedge -->
# sources/sync-backup/git-annex/doc/special_remotes/compute/git-annex-compute-wasmedge

Purpose: git-annex compute remote program that runs WebAssembly binaries from the annex using WasmEdge.

Important protocol behavior: requires at least one argument, parses inputs before the first `--`, outputs before the second `--`, and remaining values as WasmEdge arguments. Each input is requested with `INPUT`, symlinked into the working directory, and the first input becomes the wasm program. Each output is requested with `OUTPUT`.

Control flow and execution: after staging, runs `wasmedge --dir "/:<pwd>" --force-interpreter -- "$wasm" "$@"` with stdin closed and stdout/stderr discarded. `--force-interpreter` avoids ahead-of-time native execution for untrusted WASM.

State and persistence: creates directories and symlinks in the sandbox. Output files are expected to be written by the WASM program to paths supplied by git-annex.

Dependencies and integration points: POSIX shell, `realpath`, WasmEdge, and the git-annex compute remote protocol.

Risks: symlink creation uses unquoted `$(realpath "$input")`, which can break on whitespace or glob characters. Discarding stderr makes debugging hard. The sandbox depends on WasmEdge's directory preopen enforcement.

Test signals: run a deterministic WASM program through git-annex compute, verify output registration, check missing wasm, names with spaces, and ensure AOT/native execution is not used.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/doc/special_remotes/compute/git-annex-compute-wasmedge -->
