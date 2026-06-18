## sources/sync-backup/syncthing/lib/protocol/bep_index_updates.go

Purpose: typed Go representation and wire conversion for BEP index and index update messages.

Important types/functions: `Index` and `IndexUpdate` structs, each with folder/files fields and `toWire`/from-wire conversions.

Control flow and state: conversion allocates file slices and maps each `FileInfo` through `ToWire(false)` or `FileInfoFromWire`. `IndexUpdate` additionally carries a `LastSequence` value.

Dependencies and integration points: used by connections to send full indexes and incremental updates between devices. Model request tests use `IndexUpdate` to simulate remote changes.

Risks: internal DB-only fields are intentionally not sent over the wire. Schema changes require conversion updates. No nil guards for nested wire file pointers.

Test signals: broad indirect coverage through model request tests and protocol connection benchmarks.
