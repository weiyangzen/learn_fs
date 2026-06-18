# sources/object-store/rustfs/crates/protocols/src/swift/symlink.rs

Provides metadata-level Swift object symlink support. It parses symlink target headers, identifies symlink metadata, formats target headers, and supplies depth/cycle validation helpers used by the main Swift object handlers.

Important API surface: `SymlinkPath` is a hashable account/container/object tuple for visited-set loop detection. `SymlinkTarget` models a same-container or cross-container target and implements `parse`, `to_header_value`, and `resolve_container`. `extract_symlink_target()` reads `x-object-symlink-target` from request headers. `is_symlink()` and `get_symlink_target()` inspect object metadata. `validate_symlink_depth`, `check_circular_reference`, and `validate_symlink_access` enforce a maximum depth of five and reject repeated paths.

Control flow: creation-time code calls `extract_symlink_target`; if present, the target is normalized into metadata. Read/head flows in the Swift handler call `get_symlink_target`, add current path to a visited set, resolve the target container, and recursively continue until a non-symlink object or validation error is reached.

State is persisted only as user metadata under `x-object-symlink-target`. This module itself performs no I/O and owns no persistent state. It depends on `http::HeaderMap`, `HashSet`, tracing, and Swift error/result types. `object.rs` records symlink metadata during PUT, while `handler.rs` resolves chains and adds response `x-symlink-target` headers.

Risks: the parser splits on the first slash, so a same-container object name containing `/` is interpreted as `container/object`. Header value formatting always returns a container-qualified form, even for same-container targets. Validation prevents cycles only when callers maintain and pass the visited set correctly.

Tests cover target parsing, invalid empty forms, formatting, container resolution, header extraction, metadata detection, depth checks, path equality, circular reference detection, and combined validation.
