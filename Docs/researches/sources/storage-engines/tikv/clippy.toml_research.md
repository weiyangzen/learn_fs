# sources/storage-engines/tikv/clippy.toml

## Purpose
`clippy.toml` configures TiKV-specific Clippy policy, primarily banning unsafe or project-incompatible APIs.

## Important APIs, types, and functions
It sets `avoid-breaking-exported-api = false`. `[[disallowed-methods]]` bans direct thread/runtime hook APIs that bypass TiKV system hooks, unsound `time` functions, and OpenSSL APIs affected by RUSTSEC advisories. `[[disallowed-types]]` bans OpenSSL types that may reach unsound `MemBio` behavior or use-after-free paths. `[[await-holding-invalid-types]]` flags holding `dashmap::mapref::one::Ref` across `.await`.

## Control flow
Clippy reads this declarative configuration during lint runs. The Makefile's `clippy` target is the main integration path.

## State and persistence behavior
No state is written. It affects compile-time lint failures and developer workflow.

## Dependencies and integration points
It depends on Clippy support for configured lints and integrates with TiKV utility wrapper APIs, security advisory policy, and the `scripts/clippy-all` pipeline.

## Risks and edge cases
Advisory comments must stay current with dependency versions. Banning types/methods may require explicit exceptions or wrapper APIs for legitimate low-level code. The referenced reason for `openssl::x509::store::X509StoreRef::objects` mentions an older RUSTSEC ID in text while the section header cites 2023-0072, so documentation consistency should be checked.

## Test signals
`make clippy` should fail on direct use of banned methods/types and pass when wrapper APIs are used. Async tests should catch holding DashMap refs across await.
