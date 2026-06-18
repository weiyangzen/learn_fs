# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_put.py

## Purpose
Implements `tahoe put`, uploading file data from a local path or stdin to an unlinked cap, alias path, or mutable file writecap, with optional mutable format/private key parameters.

## Important APIs, Types, and Functions
`load_private_key(path)` loads a PEM RSA private key, converts it to DER signing key bytes, and URL-safe-base64 encodes it for query use. `put(options)` is the command entry point and builds the upload URL, request body, and query parameters.

## Control Flow
The command normalizes the node URL, determines whether `to_file` is a direct mutable writecap, an alias/path, or omitted unlinked upload, rejects remote paths beginning with `/`, adds `mutable=true`, `private-key`, and `format` query arguments as needed, reads either a local binary file or all of stdin into `BytesIO`, performs `PUT`, and prints the resulting cap on success.

## State and Persistence Behavior
Remote persistence is via Tahoe webapi upload/link mutation. Local persistence is none. Stdin uploads are fully buffered to provide a content length compatible with `do_http()`.

## Dependencies and Integration Points
Depends on cryptography PEM loading, Tahoe RSA helpers, Twisted `FilePath`, `common.get_alias`, `escape_path`, and `common_http`. It integrates with webapi mutable creation, unlinked upload, and path-linked upload endpoints.

## Risks and Edge Cases
Private keys are passed as URL query parameters, which is functional but sensitive to logging of URLs. Supplying a private key for immutable upload raises a generic `Exception`. Stdin buffering can consume large memory. Mutable writecap detection is hard-coded to `URI:MDMF:` and `URI:SSK:`.

## Test Signals
`test_cli.py` covers put help/basic behavior and many downstream tests use `put` to seed grid state. Mutable/private-key-specific paths require focused tests beyond the broad CLI smoke coverage.
