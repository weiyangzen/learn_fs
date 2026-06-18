# sources/object-store/garage/src/garage/cli/mod.rs

Purpose: top-level CLI module aggregator.

Important APIs/types/functions: public modules `structs`, `local`, and `remote`.

Control flow: no runtime logic.

State and persistence: none directly.

Dependencies and integration points: the main binary imports CLI structs and local/remote command implementations through this module.

Risks: minimal; module layout changes affect CLI compile paths.

Test signals: compile-time module linkage.
