# sources/object-store/garage/src/api/s3/lib.rs

## Purpose
Declares the S3 API crate/module surface. It wires tracing macros and exposes the modules that make up Garage's S3 server implementation.

## Important APIs, Types, And Functions
The file uses `#[macro_use] extern crate tracing;` and declares modules: public `api_server`, `error`, `cors`, `get`, `website`, and `xml`; private `bucket`, `copy`, `delete`, `lifecycle`, `list`, `multipart`, `post_object`, `put`, `encryption`, and `router`.

## Control Flow
No runtime control flow is defined here. Visibility controls which modules are reachable from outside the crate and which are intended only for internal dispatch.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
This is the integration root for the S3 API. Public exports indicate external consumers can use the server, error type, GET helpers, CORS/website handlers, and XML types. Private modules are still integrated internally by the API server and router.

## Risks And Test Signals
Risks are compile-time visibility and module coupling. Making modules private enforces routing through the crate's server path. There are no direct tests because behavior is entirely determined by submodules.
