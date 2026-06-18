# sources/object-store/openstack-swift/swift/common/recon.py

## Purpose
`recon.py` centralizes constants for Swift recon cache file names and the default recon cache directory. Recon files are small JSON-like operational status caches consumed by recon middleware/tools elsewhere in Swift.

## Important APIs, types, and functions
Constants include `RECON_RELINKER_FILE`, `RECON_OBJECT_FILE`, `RECON_CONTAINER_FILE`, `RECON_ACCOUNT_FILE`, `RECON_DRIVE_FILE`, and `DEFAULT_RECON_CACHE_PATH`. The only function, `server_type_to_recon_file(server_type)`, validates a server type and returns the corresponding `<server_type>.recon` filename.

## Control flow and state behavior
There is no mutable state or persistence in this module. `server_type_to_recon_file()` requires `server_type` to be a string whose lower-case value is one of `account`, `container`, or `object`; invalid values raise `ValueError`. Valid values are normalized to lower-case in the returned file name.

## Dependencies and integration points
The module has no imports. It is a shared naming point for object, container, account, drive, relinker, and recon cache code that need stable file names under `/var/cache/swift` unless configured otherwise.

## Risks and edge cases
The validation intentionally excludes `drive` and `relinker` from `server_type_to_recon_file()` even though constants exist for those recon files; callers must use constants for those. Non-string values, empty strings, and unknown server types raise a generic `ValueError('Invalid server_type')`.

## Test signals
Tests should assert case-insensitive mapping for account/container/object, rejection of drive/relinker/unknown values, rejection of non-string values, and stability of the exported constants.
