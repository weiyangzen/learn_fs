# sources/storage-engines/tikv/components/engine_panic/src/cf_names.rs

Purpose: Implements `CfNamesExt` for `PanicEngine`.

Important APIs and types: `PanicEngine::cf_names` returns `Vec<&str>` by trait contract but unconditionally panics.

Control flow and state: No state or persistence; every call is a sentinel failure.

Dependencies and integration: Depends on `engine_traits::CfNamesExt` and the local `PanicEngine`. It documents that real engines must expose column-family names.

Risks: Any call in tests or runtime will panic, as intended for this skeleton.

Test signals: No local tests; compile-time trait conformance is the signal.
