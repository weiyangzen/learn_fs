# sources/sync-backup/kopia/internal/crypto/aesgcm.go

Purpose: encrypts and decrypts byte slices using AES-256-GCM with keys derived from a master key and salt.

Important APIs/types/functions: `EncryptAes256Gcm`, `DecryptAes256Gcm`, `initCrypto`, constants `purposeAESKey` and `purposeAuthData`, and `errPlaintextTooLarge`.

Control flow: `initCrypto` derives a 32-byte AES key and 32-byte auth-data value via HKDF, builds AES and GCM. Encryption allocates nonce+ciphertext+tag, fills a random nonce, and seals with derived auth data as additional authenticated data. Decryption derives the same material, checks minimum length, copies input, splits nonce/payload, and opens in place.

State and persistence behavior: ciphertext stores the nonce prefix and GCM payload. There is no package state. Auth data binds ciphertext to master key/salt/purpose separation.

Dependencies/integration: uses `crypto/aes`, `cipher`, `rand.Reader`, `io.ReadFull`, and `DeriveKeyFromMasterKey`.

Risks/test signals: random nonce generation errors propagate. The decrypt comment says "encrypts" but implementation decrypts. No direct AES-GCM test is listed; coverage likely comes through repository encryption callers.
