# sources/storage-engines/tikv/components/resource_metering/src/error.rs

## Purpose
This file defines the crate-wide result alias for resource metering.

## Important APIs, Types, And Functions
`pub type Result<T> = std::result::Result<T, Box<dyn std::error::Error + Sync + Send>>;` standardizes fallible APIs on boxed thread-safe errors.

## Control Flow
There is no control flow beyond type aliasing. Callers can return any error implementing `Error + Send + Sync + 'static` through `?` conversions where available.

## State And Persistence Behavior
No runtime state or persistence.

## Dependencies And Integration Points
The alias depends only on the standard library and is intended for use across recorder/reporter/client modules that need heterogeneous errors.

## Risks
Boxed dynamic errors erase concrete error types, which simplifies APIs but can make matching/recovery harder.

## Test Signals
No local tests are needed for the alias.
