# sources/user-network-fs/rclone/cmd/selfupdate/verify.go

## Purpose

Build-tagged into normal self-update builds, this file verifies downloaded release archives against a signed `SHA256SUMS` file.

## Important APIs, Types, and Functions

`verifyHashsum` downloads `<site>/<version>/SHA256SUMS` and delegates to `verifyHashsumDownloaded`. `verifyHashsumDownloaded` parses the embedded `ncwPublicKeyPGP`, decodes a clearsigned checksum block, validates the detached signature with ProtonMail OpenPGP, extracts the target archive hash with `findFileHash`, and compares it to the supplied SHA-256 bytes.

## Control Flow

The path is download checksum list, parse keyring, clearsign decode, reject unsigned trailing data, check signature over `block.Bytes`, locate archive row, then reject byte inequality. Error messages distinguish key parse, missing signature, unsigned data, invalid signature, missing archive hash, and hash mismatch.

## State and Persistence Behavior

No mutable state is persisted. The trusted public key is a compiled constant, so key rotation requires source change and rebuild.

## Dependencies and Integration Points

This integrates with the broader self-update downloader and `findFileHash` in the package. It depends on `downloadFile`, `fs.Debugf`, OpenPGP clearsign parsing, and the release server checksum layout.

## Risks and Test Signals

Risks include stale signing key material, accepting a signed checksum file whose parsed archive entry is outside the signed bytes if `findFileHash` reads the wrong buffer, and strict dependency on clearsigned `SHA256SUMS` formatting. Tests in `verify_test.go` cover success, one-bit signature corruption, hash mismatch, and missing archive name.
