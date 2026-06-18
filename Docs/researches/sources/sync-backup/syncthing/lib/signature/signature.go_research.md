# sources/sync-backup/syncthing/lib/signature/signature.go

Purpose: provides PEM-based ECDSA key generation, signing, and verification for release signatures and tooling.

Important APIs and control flow: `GenerateKeys` creates an ECDSA P-521 key using Syncthing's random reader, marshals the private key with `x509.MarshalECPrivateKey`, and marshals the public key as PKIX. `Sign` loads a private key, hashes all reader data, signs the hash, ASN.1-marshals `R` and `S`, and wraps the result in a `SIGNATURE` PEM block. `Verify` loads a public key, decodes and unmarshals the PEM signature, rehashes the reader, and calls `ecdsa.Verify`. `hashReader` SHA-256 hashes reader content but returns the hex-encoded digest bytes rather than raw hash bytes; sign and verify match because both use the same representation.

State and persistence: no internal persistent state. Inputs and outputs are PEM byte slices and reader streams.

Dependencies and integration: used by upgrade verification; depends on crypto/x509, ASN.1, PEM, SHA-256, and `lib/rand`.

Risks: `loadPrivateKey` does not nil-check `pem.Decode`, so malformed private PEM can panic. The hex-encoded hash convention is nonstandard and must remain consistent with existing signatures. Tests cover happy path and wrong data, not malformed PEM.
