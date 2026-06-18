# sources/user-network-fs/rclone/backend/mailru/mrhash/mrhash.go

## Purpose
`mrhash.go` implements Mail.ru Cloud's custom checksum algorithm as a Go `hash.Hash`. The algorithm returns padded raw content for data of 20 bytes or less; for larger data it computes SHA1 over the prefix string `mrCloud`, then file data, then the decimal byte length. The package also provides one-shot sum and hex decoding helpers for backend metadata.

## Important APIs, Types, And Functions
Exports are `BlockSize`, `Size`, `ErrorInvalidHash`, `New`, `Sum`, and `DecodeString`. The private `digest` tracks bytes written, an underlying SHA1 state, and `small` content used for <=20 byte sums. `Write` forwards to SHA1, increments `total`, and appends to `small` while the total remains within `Size`. `Sum` returns padded `small` for small inputs or clones the SHA1 state with `cloneSHA1`, writes the decimal length, and returns the SHA1 sum for larger inputs.

`Reset` initializes SHA1 and writes the fixed `startString`. `Size` returns 20 and `BlockSize` returns SHA1's block size of 64. `DecodeString` hex-decodes and enforces exactly 20 bytes.

## Control Flow
Streaming callers construct a digest with `New`, call `Write` repeatedly, and call `Sum` any number of times. `Sum` is side-effect free for large files because it marshals/unmarshals the SHA1 binary state before appending the length suffix. For small files it allocates a fresh 20-byte zero-padded buffer.

## State And Persistence Behavior
All state is in the digest instance. There is no global mutable state beyond exported constants and the sentinel error. The implementation relies on `crypto/sha1` supporting `encoding.BinaryMarshaler` and `encoding.BinaryUnmarshaler`.

## Dependencies And Integration Points
The Mail.ru backend registers this constructor as the rclone `MailruHash` type and uses `DecodeString` to parse API hashes and `Sum` or streaming `New` to validate uploads/downloads. The package depends only on standard crypto, encoding, hash, hex, errors, and strconv packages.

## Risks And Edge Cases
`Reset` does not clear `small`; after writing a small value, calling `Reset`, and then summing an empty digest may include old bytes if `small` retained previous content. The tests only assert no panic after reset, not correctness of the reset result. `Write` appends an entire write when `total <= Size` after the write, so it correctly stops storing small content once the total crosses 20 bytes. `Sum` panics if SHA1 state cloning fails, which should not occur with standard `sha1.New` but is a hard failure mode.

## Test Signals
Tests validate expected hashes across boundaries around 20 bytes and large sizes, many chunk sizes, idempotent repeated `Sum`, non-panicking reset/sum behavior, `Size`, and `BlockSize`. Additional targeted coverage should assert `Reset` clears previous small data and `DecodeString` rejects bad length and malformed hex.
