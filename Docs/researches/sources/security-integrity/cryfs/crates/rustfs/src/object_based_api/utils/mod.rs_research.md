# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/utils/mod.rs

Purpose: utility module facade for object adapters.

Important APIs: exports `MaybeInitializedFs`; feature-gated `OpenFileList` and test callback; feature-gated `DirCache`, `OpenDirHandle`, `InodeList`, `FUSE_ROOT_ID`, `DUMMY_INO`, `MakeOrphanError`, and `MoveInodeError`.

Control flow and state: no runtime behavior.

Dependencies and integration: consumed by object adapters and public object API facade.

Risks and tests: utility availability depends on backend features. This file defines which internals become visible across the object-based module.
