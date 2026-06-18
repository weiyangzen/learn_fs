# sources/object-store/rustfs/crates/s3select-api/src/query/mod.rs

## Purpose
This module declares the S3 Select query API surface and defines the core `Context` and `Query` values shared by parser, dispatcher, planner, and database-manager layers.

## Important APIs, Types, And Functions
The module exports `analyzer`, `ast`, `dispatcher`, `execution`, `function`, `logical_planner`, `optimizer`, `parser`, `physical_planner`, `scheduler`, and `session`. `Context` wraps `Arc<SelectObjectContentInput>`. `Query` stores a `Context` and SQL content string with `new`, `context`, and `content` accessors.

## Control Flow
Callers construct `Query::new(Context { input }, expression)` and pass it to `DatabaseManagerSystem` or `QueryDispatcher`. The context carries the S3 Select request details needed for object-store registration and table setup.

## State And Persistence Behavior
`Query` and `Context` are cloneable in-memory request descriptors. They do not persist state or own query execution resources.

## Dependencies And Integration Points
This is the package-level query namespace. It depends on `s3s::dto::SelectObjectContentInput` and is used by `RustFSms`, `QueryStateMachine`, `SessionCtxFactory`, tests, and external S3 Select handlers.

## Risks And Edge Cases
The query content is independent from `input.request.expression`; callers must keep them consistent. The context is immutable through `Arc`, but the underlying DTO is cloned in tests and database construction.

## Test Signals
All query integration and error-handling tests construct `Query` and `Context` through this module.
