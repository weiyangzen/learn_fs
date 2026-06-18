# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/interface/file.rs

Purpose: object interface for closed regular files.

Important APIs: `File::into_node` and async `File::into_open(this, flags) -> OpenFile`.

Control flow and state: consumes an async-drop file guard to create an open-file object. This transfers future I/O to the `OpenFile` trait and lets adapters register a file handle.

Dependencies and integration: used by both object adapters for `open` and by directory `create_and_open_file`.

Risks and tests: access mode validation is up to implementations. Failure must preserve async-drop correctness for the consumed guard.
