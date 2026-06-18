# sources/security-integrity/cryfs/crates/rustfs/src/common/handles/handle_trait.rs

Purpose: common interface for handle-like numeric wrapper types usable by the handle pool, map, and forest.

Important APIs: associated constants `MIN` and `MAX`, plus `incremented` and `range(begin, end)`.

Control flow and state: the trait is behavior-only and requires clone, equality, ordering, hashing, and debug. Concrete implementations are `FileHandle`, `InodeNumber`, and `OpenDirHandle`.

Dependencies and integration: keeps handle utilities generic without relying on unstable `std::iter::Step`.

Risks and tests: correctness of allocation depends on each implementation providing monotonic `incremented` and exclusive-end `range`. The parameter name typo `end_exclusve` is cosmetic.
