<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/backup_stream.rs -->
# sources/storage-engines/tikv/components/error_code/src/backup_stream.rs

Purpose: this module declares backup-stream/log-backup error codes under the `KV:LogBackup:` namespace. It gives richer descriptions and workarounds than most other `error_code` modules, making it useful for user-facing diagnosis.

Important APIs and constants: `define_error_codes!` expands constants such as `PROTO`, `NO_SUCH_TASK`, `OUT_OF_QUOTA`, `OBSERVE_CANCELED`, `MALFORMED_META`, `IO`, `TXN`, `SCHED`, `PD`, `RAFTREQ`, `RAFTSTORE`, `GRPC`, `ENCRYPTION`, and `OTHER`, plus a module-level `ALL_ERROR_CODES` vector. Each constant is an `ErrorCode { code, description, workaround }`.

Control flow and state: this is declarative code. Runtime users import constants or iterate `ALL_ERROR_CODES`; no dynamic mapping implementation is present. The constants are lazily collected by `lazy_static` when `ALL_ERROR_CODES` is first accessed.

Dependencies and integration points: the module depends on the crate-level macro and `ErrorCode` struct. It is meant to integrate with backup stream components that translate local error variants into stable error-code values.

Risks: despite being a declared module in `lib.rs`, it is not included in `bin.rs`'s generated TOML list, so catalog generation can omit these codes. Several strings contain grammar issues but are otherwise meaningful. Since there is no `ErrorCodeExt` implementation here, correctness depends on backup-stream error types manually returning the right constants elsewhere.

Test signals: no local tests exist. Compile-time expansion of the macro is the only direct signal in this file.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/backup_stream.rs -->
