# sources/storage-engines/tikv/components/test_coprocessor/src/lib.rs

## Purpose
This crate root exposes the coprocessor test fixture API. It enables specialization, declares internal modules for schema/request/storage helpers, and re-exports their public items for test code.

## Important APIs And Integration Points
Modules are `column`, `dag`, `fixture`, `store`, `table`, and `util`. The root re-export `pub use crate::{column::*, dag::*, fixture::*, store::*, table::*, util::*};` makes builder types such as `ColumnBuilder`, `TableBuilder`, `DagSelect`, `Store`, `ProductTable`, and request helpers available directly from `test_coprocessor`.

## State And Risks
The crate uses `#![feature(specialization)]` and `#![allow(incomplete_features)]`, mostly because `store.rs` implements a default generic conversion trait with specializations. That ties this test crate to TiKV's nightly-capable build configuration. There is no runtime state in the root itself; state is owned by the submodules.

## Test Signals
Failures here are compile-time: module visibility or re-export changes can break a broad set of coprocessor tests.
