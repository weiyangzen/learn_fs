# sources/object-store/garage/src/model/helper/mod.rs

## Purpose
This file is the module index for Garage model helpers.

## Important APIs, types, and functions
It declares `bucket`, `error`, `key`, and `locked` submodules. The actual APIs are `BucketHelper`, helper `Error`, `KeyHelper`, and `LockedHelper`.

## Control flow
There is no runtime control flow in this module. It only makes helper modules available to the crate.

## State and persistence behavior
No state is stored here. Persistence behavior is implemented in the submodules.

## Dependencies and integration points
`garage.rs` exposes helper constructors through `Garage::bucket_helper`, `Garage::key_helper`, and `Garage::locked_helper`, relying on this module tree.

## Risks and edge cases
The main risk is public module organization: renaming or removing exports breaks callers throughout admin/S3/K2V code. There are no behavioral edge cases in the file itself.

## Test signals
No direct tests are needed beyond compilation.
