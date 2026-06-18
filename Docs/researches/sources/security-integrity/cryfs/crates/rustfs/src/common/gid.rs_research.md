# sources/security-integrity/cryfs/crates/rustfs/src/common/gid.rs

Purpose: lightweight typed group identifier wrapper.

Important APIs: `Gid(u32)` with `Display`, `From`, and `Into`.

Control flow and state: no behavior beyond conversion and formatting. It preserves type distinction between group IDs and raw integers.

Dependencies and integration: used in `RequestInfo`, `NodeAttrs`, object trait creation/setattr methods, and `MaybeInitializedFs` initialization. Publicly re-exported.

Risks and tests: no validation of platform-specific gid ranges beyond `u32`. Test helpers assert request gid values when checking FUSE request propagation.
