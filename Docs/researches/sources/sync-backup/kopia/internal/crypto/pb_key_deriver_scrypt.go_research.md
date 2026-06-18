# sources/sync-backup/kopia/internal/crypto/pb_key_deriver_scrypt.go

Purpose: registers and implements scrypt password-based key derivation.

Important APIs/types/functions: `ScryptAlgorithm`, `scryptMinSaltLength`, `scryptKeyDeriver`, init registration, and `deriveKeyFromPassword`.

Control flow: init registers algorithm `scrypt-65536-8-1` with N=65536, r=8, p=1, and a 16-byte minimum salt. Derivation rejects short salts and calls `scrypt.Key`.

State and persistence behavior: only global registry mutation at init. Derived key bytes are returned to the caller.

Dependencies/integration: used by `DeriveKeyFromPassword`; imports `golang.org/x/crypto/scrypt` and `pkg/errors`.

Risks/test signals: scrypt memory/CPU cost is substantial and can affect unlock performance. No direct tests listed here cover vectors, salt rejection, or unsupported key sizes.
