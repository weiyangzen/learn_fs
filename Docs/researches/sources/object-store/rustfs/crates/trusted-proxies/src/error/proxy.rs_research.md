# sources/object-store/rustfs/crates/trusted-proxies/src/error/proxy.rs

Purpose: Defines proxy validation errors and recoverability semantics.

Important APIs: `ProxyError` variants cover malformed XFF/RFC7239 headers, chain validation failure, chain-too-long, untrusted proxy, non-continuity, IP/header parse failures, timeout, and internal errors. Helper constructors create common variants. `From<AddrParseError>` maps to `IpParseError`.

Control flow: `is_recoverable` returns true for untrusted proxy, chain too long, non-continuity, and timeout, enabling middleware fallback to direct peer. Malformed headers, parse errors, chain validation failure, and internal errors are non-recoverable.

State and dependencies: Error-only module with `thiserror` and `AddrParseError`.

Integration points: `ProxyValidator`, `ProxyChainAnalyzer`, middleware fallback path, metrics failure labels, and `AppError` conversion.

Risks and tests: Treating `ChainTooLong` as recoverable means a suspicious oversized proxy header can be downgraded to direct peer rather than rejected. Unit validator tests assert `ChainTooLong` is produced by analyzer, but recoverability behavior is not directly asserted.
