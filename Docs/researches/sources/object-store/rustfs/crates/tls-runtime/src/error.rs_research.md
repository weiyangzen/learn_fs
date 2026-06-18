## sources/object-store/rustfs/crates/tls-runtime/src/error.rs

Purpose: defines the shared error type for TLS runtime operations.

Important APIs/types/functions: `TlsRuntimeError` variants cover empty source path, missing directory, non-directory path, material errors, publication errors, and wrapped IO errors. `thiserror::Error` supplies display messages and source handling for IO.

Control flow and state: no state; errors are constructed by source validation, material loading, and coordinator/consumer publication paths.

Dependencies and integration points: used across `source`, `material`, `coordinator`, and server resolver code. Target TLS validation converts lower-level parsing errors into `TargetError` instead of this type, but shared runtime paths use it directly.

Risks: `Material(String)` and `Publication(String)` are flexible but lose structured detail. Directory errors include full local paths, which is useful for operators but may need care in externally exposed APIs.

Test signals: source validation tests assert `DirectoryNotFound`; other variants are exercised indirectly by cert/material tests.
