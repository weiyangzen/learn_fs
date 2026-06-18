# sources/object-store/garage/src/format-table/Cargo.toml

Purpose: declares the tiny `format_table` helper crate used by CLI output.

Important APIs/types/functions: configures `lib.rs`, version `0.1.1`, edition 2018, AGPL-3.0, no explicit dependencies.

Control flow: build-time manifest only.

State and persistence: none.

Dependencies and integration points: consumed heavily by `garage` CLI remote command modules for human-readable tables.

Risks: the crate's simple API means formatting behavior changes can affect many CLI snapshots/manual workflows. No dependency surface limits build risk.

Test signals: no direct manifest tests.
