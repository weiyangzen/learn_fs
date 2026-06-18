# sources/distributed-fs/tahoe-lafs/src/allmydata/codec.py

## Purpose

This module wraps zfec's Cauchy Reed-Solomon erasure codec behind Tahoe-LAFS encoder/decoder interfaces and Deferred-friendly async methods.

## Important APIs, Types, And Functions

`CRSEncoder` implements `ICodecEncoder`. `set_params()` records data size and share counts, computes share size and padding, and creates `zfec.Encoder`. `encode()` validates input share sizes and desired IDs, then runs zfec encoding in the CPU threadpool. `CRSDecoder` implements `ICodecDecoder`; `set_params()` computes chunk/share sizing and creates `zfec.Decoder`, `get_needed_shares()` returns k, and `decode()` validates counts and runs zfec decode in the threadpool. `parse_params()` parses serialized `data-required-max` bytes.

## Control Flow

Callers configure an encoder/decoder with data size, required shares, and max shares. Encoding optionally defaults desired share IDs to all shares and returns `(shares, desired_share_ids)`. Decoding requires exactly the needed number of shares and corresponding IDs, then returns reconstructed data chunks from zfec.

## State And Persistence

Encoder/decoder instances keep sizing parameters and a zfec object. There is no persistence; serialized parameters are returned for storage in higher-level share metadata.

## Dependencies And Integration Points

It depends on `zfec`, Tahoe math/assert/deferred utilities, the CPU threadpool, and Tahoe codec interfaces. Immutable upload/download code uses this layer for CPU-heavy erasure coding without blocking the reactor.

## Risks

The code uses assertions for some invariants and `precondition()` for others. `encode_proposal()` is unimplemented. `parse_params()` trusts the byte format and can raise generic exceptions. Threadpool offload is required for reactor health; calling zfec directly elsewhere would risk blocking.

## Test Signals

Round-trip encode/decode with multiple k/n settings, desired share subsets, invalid share counts, invalid share lengths, parameter serialization parsing, and reactor responsiveness under large encode/decode operations.
