# sources/object-store/garage/src/model/lib.rs

## Purpose
This file is the crate root for `garage_model`. It declares exported model modules and enables tracing macros.

## Important APIs, types, and functions
It exports `permission`, `index_counter`, admin/bucket/key tables, optional `k2v`, `s3`, `garage`, `helper`, and `snapshot`.

## Control flow
There is no runtime control flow. Conditional compilation exposes `k2v` only when the feature is enabled.

## State and persistence behavior
No state is stored here. State and persistence are implemented in the exported modules.

## Dependencies and integration points
Other Garage crates import table types, `Garage`, helpers, S3 metadata models, and optional K2V models through this crate root.

## Risks and edge cases
Changing module names or feature gates is a public crate API change. The `#[macro_use] extern crate tracing;` pattern makes logging macros available throughout the crate.

## Test signals
Compilation under normal and `k2v` feature configurations is the main signal.
