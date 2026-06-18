# sources/object-store/garage/src/model/s3/mod.rs

## Purpose
This file declares S3 metadata submodules for the Garage model crate.

## Important APIs, types, and functions
It exports `block_ref_table`, `mpu_table`, `object_table`, `version_table`, and `lifecycle_worker`.

## Control flow
There is no runtime logic here.

## State and persistence behavior
No direct state. The exported modules define S3 object, multipart, version, block-ref, and lifecycle persistence.

## Dependencies and integration points
`garage.rs` imports these modules to construct S3 metadata tables and workers. S3 API crates import the data models through this module tree.

## Risks and edge cases
Module organization changes affect many S3 code paths.

## Test signals
Compilation is the relevant signal.
