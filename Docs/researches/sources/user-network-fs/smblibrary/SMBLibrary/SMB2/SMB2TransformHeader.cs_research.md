# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/SMB2TransformHeader.cs

## Purpose

Implements the SMB 3.x transform header used for encrypted SMB2 messages. It carries the transform protocol id, authentication signature, nonce, original plaintext size, encryption flags/algorithm field, and session id.

## Important APIs, Types, And Functions

`SMB2TransformHeader(byte[], int)` parses a 52-byte transform header, `WriteBytes` writes the protocol id and signature plus associated data, `GetAssociatedData` returns the nonce-through-session-id span for AEAD authentication, and `IsTransformHeader` checks the `0xFD 'SMB'` signature.

## Control Flow

Outbound writing places the first 20 bytes separately, then delegates to `WriteAssociatedData` for the nonce, original size, reserved field, flags, and session id. Inbound parsing reads the same fixed offsets.

## State And Persistence Behavior

No durable state is stored here; this is per-message encryption metadata consumed by encryption/decryption and session lookup.

## Dependencies And Integration Points

Depends on `Utilities` byte helpers and `SMB2TransformHeaderFlags`. It is an integration point between SMB 3.x encryption code and session key material.

## Risks And Edge Cases

The default constructor initializes only `ProtocolId`; callers must set `Signature` and `Nonce` before writing or `ByteWriter` can fail. `IsTransformHeader` does not check buffer length. The flags field is overloaded with algorithm semantics for older dialects, so dialect-specific validation belongs above this class.

## Test Signals

Round-trip tests should cover full header serialization, associated-data bytes excluding signature/protocol id, short-buffer failure behavior, and AES-CCM/GCM session-id lookup paths.

Source-read signal: reviewed the complete local source file for this item.
