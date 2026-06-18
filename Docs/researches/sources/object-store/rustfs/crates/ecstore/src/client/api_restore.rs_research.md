# sources/object-store/rustfs/crates/ecstore/src/client/api_restore.rs

## Purpose
Provides the transition client API for S3 restore-object requests, plus small serializable structures for restore output location/encryption metadata.

## Important APIs, types, and functions
`Encryption`, `MetadataEntry`, and `S3` model restore destination attributes. `TransitionClient::restore_object` is the only behavior-bearing function. It accepts bucket, object, optional version id, and an `s3s::dto::RestoreRequest`.

## Control flow
The method builds query values containing `restore` and optional `versionId`, prepares an empty request body, and calls `execute_method`. It then reads the full response body. HTTP `202 Accepted` and `200 OK` are considered success; any other status is converted through `http_resp_to_error_response`.

## State and persistence behavior
There is no local persistence. Successful calls instruct the remote tier to start or update object restore state. The supplied `RestoreRequest` is not currently serialized; the code has commented `quick_xml` serialization and sends an empty body/hash instead.

## Dependencies and integration points
This module integrates with `TransitionClient`, `RequestMetadata`, `ReaderImpl`, S3 restore DTOs, and shared error conversion. It is expected to be used by object lifecycle or tiering code that needs to restore archived objects from remote storage classes.

## Risks and edge cases
The HTTP method is `HEAD`, while S3 RestoreObject is normally a POST request with a restore XML body. The current empty payload and empty checksum fields mean restore parameters such as days, tier, select type, or output location are ignored. This is likely incomplete or non-compliant unless the target tier has custom semantics.

## Test signals
No local tests are present. Useful tests would assert POST method selection, XML body serialization, version-id query encoding, checksum headers, and 200/202/error response handling against a local S3-compatible endpoint.
