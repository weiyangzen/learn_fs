# sources/distributed-fs/tahoe-lafs/src/allmydata/test/web/test_webish.py

## Purpose

This module tests lower-level `allmydata.webish` request and site behavior that sits below the larger WebAPI tests: multipart form parsing, request body storage policy, and access-log capability censoring.

## Important APIs, types, and functions

- `TahoeLAFSRequestTests._fields_test` builds a `TahoeLAFSRequest` over a Twisted `DummyChannel`, injects headers/body bytes, calls `requestReceived`, and matches the resulting `request.fields`.
- `test_no_form_fields` asserts GET requests do not populate `fields`.
- `test_form_fields_if_filename_set` and `test_form_fields_if_name_is_file` verify multipart POST parsing and bytes-vs-text behavior for file-like fields.
- `test_form_fields_require_correct_mime_type` ensures non-`multipart/form-data` POST bodies are not parsed as form fields, a regression check for ticket 3854.
- `TahoeLAFSSiteTests._test_censoring` creates a `TahoeLAFSSite`, sends a dummy request, and verifies the access log contains a censored path rather than raw capabilities or private key material.
- Censoring tests cover `private-key`, `/uri/<CAP>`, `/file/<CAP>`, `/named/<CAP>`, and `/uri?uri=<CAP>`.
- `_create_request` builds a request attached to a site whose temporary-file factory creates named files in a test directory, making body-storage decisions observable.
- `test_small_content`, `test_unknown_request_size`, and `test_large_request` validate the 1 MiB threshold for memory vs temporary file request content.
- `param`, `body`, `_field`, `_multipart_formdata`, and `multipart_formdata` generate simple multipart form-data payloads for the tests.

## Control flow

Request parsing tests manually drive Twisted request lifecycle methods: `gotLength`, `handleContentChunk`, and `requestReceived`. They do not start a network listener. Access-log tests instantiate `TahoeLAFSSite`, attach it to a dummy channel/factory, receive a request path, then inspect the log file. Body-size tests call `gotLength` and inspect whether the request uses `BytesIO` or creates a temporary file.

## State and persistence behavior

The only durable state is temporary: access logs at `mktemp()` paths and named temporary files in a test directory. Small request bodies stay in memory (`BytesIO`). Unknown-size and >=1 MiB bodies are written through the site's configured temporary-file factory.

## Dependencies and integration points

The module uses Hypothesis for size property tests, testtools matchers for structural assertions, Twisted `DummyChannel`/`Resource`/`FilePath`, and `SyncTestCase`. It directly imports `TahoeLAFSRequest`, `TahoeLAFSSite`, and `anonymous_tempfile_factory`, so it is a focused contract for `webish` internals used by the full WebAPI server.

## Risks and edge cases

- Censoring must keep pace with every URL shape that can carry capabilities or private keys; this file covers common forms but not every future query parameter.
- Multipart tests use a minimal hand-built serializer, which is useful for clarity but does not cover all multipart syntax variants.
- The memory/file body threshold is tested around the 1 MiB boundary; changes to Twisted request internals or site factory wiring could break assumptions.

## Test signals

Strong signals: request form parsing, non-form POST safety, sensitive data censoring in logs, and large-body spillover behavior. Remaining gaps: full HTTP server integration, malformed multipart bodies, and access-log formats beyond the tested paths.
