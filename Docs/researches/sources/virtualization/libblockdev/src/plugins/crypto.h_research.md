# File Research: sources/virtualization/libblockdev/src/plugins/crypto.h

## Role

`crypto.h` is the public libblockdev crypto plugin API. It declares error domains, technology/mode enums, public data structs, keyslot context constructors, and all crypto operations implemented in `crypto.c`.

## Public Error Model

The header defines `BDCryptoError`, covering unavailable technologies, device/state errors, invalid specs/parameters/context, LUKS format/resize/convert failures, key add/remove/keyslot errors, escrow/NSS/cert failures, kernel keyring failures, and keyfile failures.

The error domain is exposed through `bd_crypto_error_quark()` and `BD_CRYPTO_ERROR`.

## Technology and Mode Enums

`BDCryptoTech` covers:

- LUKS
- TrueCrypt/VeraCrypt
- Escrow
- Integrity
- BitLocker
- Keyring
- FileVault2
- SED OPAL

`BDCryptoTechMode` exposes operation families: create, open/close, query, add/remove key, resize, suspend/resume, backup/restore, and modify.

These enums are used by `bd_crypto_is_tech_avail()`.

## Public Data Structures

The header defines configuration and result structs for:

- LUKS PBKDF parameters: type, hash, memory, iterations, time, and parallel threads.
- LUKS extra format parameters: alignment, detached data device, integrity, sector size, label, subsystem, PBKDF.
- dm-integrity extra parameters: sector size, journal size/watermark/commit time, interleave sectors, tag size, buffer sectors.
- LUKS info: version, cipher, mode, UUID, backing device, sector size, metadata size, label, subsystem, and hardware encryption type.
- BitLocker info: cipher, mode, UUID, backing device, sector size.
- Integrity info: algorithm, key size, sector/tag/interleave sizes, journal size, journal crypto/integrity algorithms.
- LUKS token info: token ID, token type, assigned keyslot.

Each heap-owning struct has copy/free helpers.

## Keyslot Context API

The header keeps `BDCryptoKeyslotContext` opaque and exposes constructors for:

- Passphrase bytes.
- Keyfile path with offset and size.
- Kernel keyring key description.
- Raw volume key bytes.

This keeps secret representation private to the implementation while allowing introspection bindings to pass context objects.

## LUKS API Surface

Declared LUKS functions include:

- detection and status
- format/open/open_flags/close
- add/remove/change key
- resize, suspend, resume
- kill slot
- header backup/restore
- set/check label and subsystem
- set UUID
- convert LUKS version
- set persistent activation flags
- info and token info

The header also defines LUKS persistent activation flags and hardware encryption type values.

## Non-LUKS API Surface

The header declares:

- Integrity format/open/close/info.
- Kernel keyring add.
- encrypted-looking heuristic.
- TrueCrypt/VeraCrypt open/open_flags/close.
- BitLocker open/open_flags/close/info.
- FileVault2 open/open_flags/close.
- Escrow device packet creation.
- OPAL support check, wipe, reset, and OPAL-backed LUKS format.

## Notable Risks

- The public API spans multiple cryptsetup feature generations, so ABI/API compatibility matters.
- Some parameters are documented as bytes while cryptsetup often uses sectors or bits internally; callers must follow the header documentation.
- OPAL and escrow functions may exist even when compile-time support is unavailable; callers must check availability and errors.
