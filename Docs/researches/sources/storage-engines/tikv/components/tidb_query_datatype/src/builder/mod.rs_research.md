# sources/storage-engines/tikv/components/tidb_query_datatype/src/builder/mod.rs

## Purpose
Defines the public builder namespace for query datatype helper constructors.

## APIs, Flow, And State
The module declares `field_type` and re-exports `FieldTypeBuilder`. There is no runtime control flow or stored state beyond Rust module resolution.

## Dependencies And Integration
Integrated by consumers importing `tidb_query_datatype::builder::FieldTypeBuilder`. It hides the concrete file layout and gives the crate a stable builder surface.

## Risks And Test Signals
Risk is minimal. Any missing or broken re-export is caught by compilation of callers and tests using the builder API.
