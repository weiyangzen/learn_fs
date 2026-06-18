# sources/object-store/garage/src/garage/cli/local/mod.rs

Purpose: local CLI module aggregator.

Important APIs/types/functions: declares `completions`, `convert_db`, `init`, and `repair` as crate-private submodules.

Control flow: no runtime logic.

State and persistence: none directly.

Dependencies and integration points: imported by `garage/cli/mod.rs` and command dispatch code.

Risks: module visibility is crate-private; moving public APIs here could expose unwanted surface.

Test signals: compile-time module linkage only.
