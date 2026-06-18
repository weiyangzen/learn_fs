# sources/security-integrity/cryfs/crates/check/src/error/wrong_parent_pointer.rs

Purpose: This file defines the corruption error for a readable blob whose stored parent pointer does not match any blob that references it.

Important APIs and flow: `WrongParentPointerError` stores `blob_id`, `blob_type`, `parent_pointer`, and all `referenced_as` paths. `Display` renders a blob display message with readable blob info containing the mismatched parent pointer.

State and persistence: The error captures observed blob metadata and incoming references. It is deterministic through `BTreeSet`.

Dependencies and integration: It is produced by `CheckParentPointers` during finalization and included in `CorruptedError`.

Risks and test signals: Tests cover file, dir, symlink, no references, and many references. The error message text has a minor grammar issue ("blobs parent pointer") but is consistently asserted. It does not yet assert entry type mismatches beyond parent pointer mismatch.
