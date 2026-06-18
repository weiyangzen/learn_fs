# sources/object-store/rustfs/crates/targets/src/runtime/s3_hooks.rs

## Purpose
Registry scaffold for S3 post-auth hook extensions. It validates extension schemas and hook contracts, records hook registrations by hook point, and currently dispatches with an allow/continue decision only.

## Important APIs, types, and functions
- `S3HookRegistryError` reports invalid contracts, unsupported extension kinds, and missing hook capability.
- `S3HookRegistration` records extension id and hook point.
- `S3HookRegistry` stores registrations by `S3HookPoint`.
- `S3HookContext::post_auth` constructs context only when an authenticated principal is present.
- `S3HookDecision::Continue` is the current dispatch result.

## Control flow
`register_schema` rejects non-S3-hook schemas, requires the post-auth hook capability, validates the hook contract, and registers all declared hook points. `dispatch_post_auth` ignores current registrations and context and returns `Continue`, preserving existing request behavior while the registry contract is introduced.

## State and persistence behavior
State is an in-memory `BTreeMap` of hook registrations. No hook side effects, persistence, or request mutation occurs in this file.

## Dependencies and integration points
It depends on `rustfs_extension_schema` extension kinds, capabilities, hook points, and S3 hook contract validation. It is re-exported by `lib.rs` for S3 server/runtime integration.

## Risks and edge cases
Dispatch is a placeholder; registering hooks does not yet execute plugin code. `S3HookContext::post_auth` only rejects blank principals and does not validate bucket/object strings. Multiple hooks per hook point are accepted without ordering guarantees beyond `Vec` insertion order within a surface.

## Test signals
Tests verify empty registry behavior, blank-principal rejection, valid builtin hook registration with unchanged continue dispatch, rejection of non-hook schemas, and rejection of unsafe contracts such as IAM bypass.
