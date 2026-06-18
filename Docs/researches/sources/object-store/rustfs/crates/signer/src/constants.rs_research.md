# sources/object-store/rustfs/crates/signer/src/constants.rs

## Purpose
Holds shared signing constants: unsigned payload sentinels, worker count, SigV4 algorithm name, and a timestamp format.

## Important APIs
`UNSIGNED_PAYLOAD` and `UNSIGNED_PAYLOAD_TRAILER` are S3 signing sentinel strings. `SIGN_V4_ALGORITHM` is `AWS4-HMAC-SHA256`. `ISO8601_DATEFORMAT` is a `time` format item slice for millisecond-style UTC timestamps. `TOTAL_WORKERS` is a crate-level numeric constant set to 4.

## Integration and Risks
The constants are consumed by signer modules, especially SigV4 payload handling. Timestamp format includes subsecond output; other signer code uses compact `YYYYMMDDTHHMMSSZ` for AWS canonical strings, so callers should not assume this constant is valid for every SigV4 field. `TOTAL_WORKERS` is not visibly tied to signing logic in the read files and may be legacy.

## Test Signals
No local tests in this file; correctness is indirectly tested by SigV4 module examples.
