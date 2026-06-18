# sources/object-store/rustfs/crates/ecstore/src/event/targetid.rs

Purpose: This file defines a minimal target identifier type for event notification targets. It appears to be an early or compatibility scaffold for MinIO-style target IDs.

Important APIs and types: `TargetID` stores private `id: String` and `name: String` fields. Its only method is a private inherent `to_string(&self) -> String` that formats `id:name`.

Control flow: There is no external construction or dispatch logic in this file. Formatting is a simple string interpolation when the private method is called inside the module, though no current target file calls it.

State and persistence behavior: `TargetID` is an in-memory value only. It derives no `Clone`, `Debug`, `Eq`, `Hash`, or serde traits, so it is not currently usable as the active map key hinted by commented code in `targetlist.rs`.

Dependencies and integration points: `targetlist.rs` imports `TargetID` and uses it in an unused private `TargetIDResult` struct. The commented target map in `TargetList` suggests future integration with concrete event targets and per-target stats.

Risks: The inherent `to_string` method is private and does not implement `Display`, so callers cannot use standard formatting or `ToString`. Private fields and lack of constructor make the type impossible to construct outside this module. If it becomes a hash-map key, it will need equality and hash implementations plus careful parsing rules for IDs or names containing `:`.

Test signals: There are no tests. Current compile success only proves that the unused scaffold type is syntactically valid.
