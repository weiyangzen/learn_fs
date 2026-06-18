# sources/user-network-fs/impacket/impacket/dcerpc/v5/icpr.py

## Purpose

`icpr.py` implements the [MS-ICPR] ICertPassage Remote Protocol for submitting certificate requests to Microsoft Certificate Services. It wraps `CertServerRequest`, prepares request and attribute blobs, interprets disposition codes, and returns encoded issued certificate bytes when available.

## Important APIs, Types, And Functions

The module exports `MSRPC_UUID_ICPR`, extends Kerberos PKINIT error message mappings, defines `DCERPCSessionError`, `CERTTRANSBLOB`, `CertServerRequest`, `CertServerRequestResponse`, `translate_error_code`, and `hCertServerRequest`. `CERTTRANSBLOB` models a counted byte pointer. `CertServerRequest` is opnum 0 and sends flags, CA authority, request ID, attributes, and CSR bytes.

## Control Flow

At import time, the module adds PKINIT-related Kerberos error messages if missing. `hCertServerRequest` joins attributes with newline separators, null-terminates and UTF-16LE encodes them, builds blobs for attributes and CSR, constructs a request with `dwFlags` 0 and a null-terminated CA name, and calls `dce.request()`. It logs success for disposition 3, pending approval for disposition 5, and translated or server-provided error details otherwise. It returns joined bytes from `pctbEncodedCert['pb']`.

## State And Persistence Behavior

The module mutates the process-global Kerberos error message dictionary at import. There is no file persistence. Remote state can change because certificate requests may be created, issued, or left pending on the CA. Returned certificate blobs and disposition messages remain in memory.

## Dependencies And Integration Points

Dependencies include Impacket HRESULT errors and logging, common dtypes, NDR classes, Netlogon `checkNullString`, `DCERPC_v5` typing, Kerberos constants, UUID helpers, and `typing.List`. It integrates with AD CS tooling and PKINIT-related workflows.

## Risks And Edge Cases

This helper can request AD CS certificates and has privilege-escalation relevance when CA templates or permissions are weak. It does not raise on non-success dispositions; callers may receive empty certificate bytes. Unknown error logging decodes server disposition messages as UTF-16LE and can fail on malformed data. `base64` is imported but unused, and test coverage is marked TODO.

## Test Signals

Tests should mock `dce.request()` for success, pending, known HRESULT errors, unknown errors with disposition messages, empty cert blobs, and malformed messages. Serialization tests should verify UTF-16LE attributes, CA null termination, CSR byte counts, and request ID propagation. Integration tests require AD CS and should avoid logging sensitive CSR data.
