# sources/object-store/rustfs/crates/trusted-proxies/src/proxy/mod.rs

Purpose: Proxy validation module aggregator.

Important APIs: Declares `cache`, `chain`, `metrics`, and `validator`, then publicly re-exports all of them.

Control flow and state: Compile-time wiring only. Exposes cache stats, chain analyzer, metrics collector, `ClientInfo`, and `ProxyValidator` through a single module and crate root.

Dependencies and integration: `lib.rs` re-exports this module; middleware and tests import proxy types through crate root.

Risks and tests: Wildcard re-export makes internal-ish helpers such as `ProxyChainAnalyzer` public. Unit validator tests import both analyzer and validator, confirming these exports compile.
