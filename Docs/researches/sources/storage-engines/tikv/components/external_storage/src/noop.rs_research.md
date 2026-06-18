<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/external_storage/src/noop.rs -->
# sources/storage-engines/tikv/components/external_storage/src/noop.rs

Purpose: this module implements a no-op `ExternalStorage` backend, mainly for tests and plumbing paths that need to consume streams without persisting objects.

Important APIs and types: `NoopStorage` is `Clone + Default`. `url_for` returns `noop:///`. The `ExternalStorage` implementation reports name `noop`, consumes all bytes on `write`, returns empty readers for `read` and `read_part`, returns an empty stream for `iter_prefix`, and returns success for `delete`.

Control flow: `write` copies the input reader to `tokio::io::sink()` rather than ignoring it. This is important because upstream wrappers such as checksum readers rely on the stream being fully consumed.

State and persistence behavior: no data is stored. Reads always return EOF, listings are empty, and deletes are idempotent no-ops.

Dependencies and integration points: it uses `tokio::io`, futures streams/futures, and `tokio-util` compatibility adapters. It is selected by `make_noop_backend`/`create_storage`.

Risks: because writes succeed and reads return empty data, accidentally using noop in production could silently discard backups or exports. It should remain clearly test-oriented. Content length is ignored.

Test signals: tests verify that writing succeeds, reading returns empty data, and the backend URL is `noop:///`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/external_storage/src/noop.rs -->
