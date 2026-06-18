# sources/security-integrity/cryfs/crates/rustfs/src/common/uid.rs

Purpose: lightweight typed user identifier wrapper.

Important APIs: `Uid(u32)` with `Display`, `From`, and `Into`.

Control flow and state: no behavior beyond conversion and formatting.

Dependencies and integration: used in `RequestInfo`, `NodeAttrs`, object creation and setattr methods, and filesystem initialization. Re-exported publicly.

State and persistence behavior: the wrapper itself is not persisted, but values flow into persistent metadata through `NodeAttrs` and into newly created nodes through directory creation APIs. `MaybeInitializedFs` also uses the first request uid to construct the backend filesystem, so this tiny type participates in initialization identity.

Risks and tests: no platform-specific validation. Tests assert request uid propagation through the FUSE path. Because the wrapper is a transparent newtype over `u32`, backend code still needs to enforce any platform or filesystem ownership policy outside this file.
