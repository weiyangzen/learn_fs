# sources/storage-engines/tikv/components/engine_traits/src/cf_names.rs

Purpose: Declares the minimal trait for engines that can report their column-family names.

Important APIs and control flow: `CfNamesExt::cf_names` returns the engine's CF names as borrowed string slices.

State, persistence, and dependencies: State comes from the implementing engine's column-family registry or manifest; this trait only exposes it.

Integration points, risks, and test signals: Required by `KvEngine`, compaction helpers, delete-range helpers, and tests that iterate all CFs. Risks are ordering expectations, missing default CF, and stale CF lists after drops. Shared tests check default-only and `ALL_CFS` name exposure.
