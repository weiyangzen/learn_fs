# sources/object-store/garage/src/garage/cli/local/convert_db.rs

Purpose: implements an offline CLI for converting Garage metadata databases between supported engines.

Important APIs/types/functions: `ConvertDbOpt`, `OpenDbOpt`, `OpenLmdbOpt`, and `do_conversion`.

Control flow: structopt parses input path/engine and output path/engine. `do_conversion` rejects same-engine conversion, builds `OpenOpt` with optional LMDB map size, opens both DBs, and calls `output.import(&input)`.

State and persistence: reads one metadata database and writes a new one. Destination must be empty because `Db::import` rejects existing trees.

Dependencies and integration points: uses `garage_db::{Engine, OpenOpt, open_db, Db::import}` and `bytesize` for LMDB map-size parsing. Integrated into local CLI options.

Risks: conversion is broad and uses one transaction per tree, which can be costly for large metadata. It shares the same open options for input and output, so LMDB map size applies to both when relevant. It does not expose Fjall block-cache or fsync options.

Test signals: no direct tests; relies on DB adapter tests and manual conversion validation.
