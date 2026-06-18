# sources/object-store/rustfs/crates/ecstore/src/event/mod.rs

Purpose: This is the public event module root for ecstore. It exposes the event compatibility and target bookkeeping submodules under `crate::event`.

Important APIs and types: The file declares `pub mod name`, `pub mod targetid`, and `pub mod targetlist`. It does not define functions or data itself.

Control flow: There is no runtime control flow. Consumers import through paths such as `crate::event::name::EventName`, `crate::event::targetid::TargetID`, and `crate::event::targetlist::TargetList`.

State and persistence behavior: The module root owns no state and persists nothing.

Dependencies and integration points: `event_notification.rs` depends on `targetlist::TargetList`, while lifecycle, replication, and set-disk code use the event notification API that sits beside this module. `name.rs` keeps old `rustfs_ecstore::event::name::EventName` imports working while delegating the canonical enum to `rustfs_s3_types`.

Risks: Because this file only re-exports submodules, the main compatibility risk is removing or renaming one of these module paths. The underlying event implementation is still skeletal, so the module surface can look more complete than the runtime behavior behind it.

Test signals: There are no direct tests for this module root. Compilation of downstream imports is the primary signal.
