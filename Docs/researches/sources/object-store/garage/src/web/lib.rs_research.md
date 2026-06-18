<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/web/lib.rs -->
# sources/object-store/garage/src/web/lib.rs

## Purpose
Crate root for Garage S3 website serving.

## Important APIs, types, and functions
Enables tracing macros, declares private `error` and `web_server` modules, and publicly re-exports `Error` and `WebServer`.

## Control flow
No runtime control flow; this defines the crate's public surface.

## State and persistence behavior
No state or persistence.

## Dependencies and integration points
Consumers construct and run `WebServer` from this crate during Garage startup when `s3_web` is configured.

## Risks and test signals
Changing re-exports breaks dependent startup code. Workspace compile is the main signal.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/web/lib.rs -->
