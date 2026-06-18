# sources/object-store/rustfs/crates/s3select-api/src/server/mod.rs

## Purpose
This module exposes the server-facing database manager namespace for the API crate.

## Important APIs, Types, And Functions
It declares `pub mod dbms;`, making `DatabaseManagerSystem` and `QueryHandle` available as `server::dbms`.

## Control Flow
No local logic exists. It is a namespace boundary.

## State And Persistence Behavior
No state is held or persisted.

## Dependencies And Integration Points
Consumers import `rustfs_s3select_api::server::dbms` from here. `rustfs-s3select-query` implements the exported trait.

## Risks And Edge Cases
Any future server modules must be explicitly exported here.

## Test Signals
No local tests; all DBMS tests go through the query crate.
