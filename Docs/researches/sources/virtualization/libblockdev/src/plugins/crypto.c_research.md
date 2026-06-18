# File Research: sources/virtualization/libblockdev/src/plugins/crypto.c

## Role

`crypto.c` implements libblockdev's crypto plugin. It is a GLib/libcryptsetup wrapper for encrypted block-device operations, exposing high-level APIs for:

- LUKS1/LUKS2 format, open, close, resize, suspend/resume, key management, header backup/restore, labels, UUIDs, conversion, persistent activation flags, token info, and hardware encryption metadata.
- dm-integrity format/open/close/query.
- TrueCrypt/VeraCrypt candidate detection and activation.
- BitLocker and FileVault2 activation/query where supported by libcryptsetup.
- Linux kernel keyring insertion.
- Optional LUKS escrow packet generation through NSS and `volume_key`.
- Optional OPAL self-encrypting drive support through libcryptsetup 2.7+ and Linux OPAL ioctls.

The file is security-sensitive because it handles passphrases, volume keys, keyfiles, kernel keyring operations, destructive formatting, keyslot removal, OPAL wipes, and PSID resets.

## Data Object Lifecycle

The file provides copy/free/new helpers for public structs declared in `crypto.h`:

- `BDCryptoLUKSPBKDF`
- `BDCryptoLUKSExtra`
- `BDCryptoIntegrityExtra`
- `BDCryptoLUKSInfo`
- `BDCryptoBITLKInfo`
- `BDCryptoIntegrityInfo`
- `BDCryptoLUKSTokenInfo`
- opaque `BDCryptoKeyslotContext`

Secret-bearing keyslot contexts are explicitly zeroed before free for passphrase and volume-key buffers via `explicit_bzero()`. Keyfile paths and keyring descriptions are normal GLib strings.

## Initialization and Capability Gating

`bd_crypto_init()` configures cryptsetup logging, enables cryptsetup debug under `DEBUG`, and creates a C locale for stable `strerror_l()` output. `bd_crypto_close()` frees the locale and clears callbacks/debug state.

`bd_crypto_is_tech_avail()` is compile-time and mode based rather than probing devices. It validates that each technology is requested only with supported modes:

- LUKS supports create, open/close, query, add/remove key, resize, suspend/resume, backup/restore, and modify.
- TrueCrypt/VeraCrypt supports open/close.
- Escrow requires `WITH_BD_ESCROW` and supports create.
- Integrity supports create, open/close, and query.
- BitLocker supports open/close and query.
- Keyring supports add-key.
- FileVault2 requires `LIBCRYPTSETUP_26`.
- OPAL requires `LIBCRYPTSETUP_27` and Linux OPAL support.

## Keyslot Contexts

The internal `BDCryptoKeyslotContext` supports passphrase, keyfile, keyring, and volume-key variants.

Public constructors validate non-empty passphrase and volume-key buffers, but keyfile and keyring constructors simply copy supplied metadata. Each crypto operation then enforces the context types it supports. Examples:

- LUKS format: passphrase or keyfile.
- LUKS open: passphrase, keyfile, or keyring.
- LUKS add/change/remove key: passphrase or keyfile.
- Integrity format/open: volume key only.
- TrueCrypt/VeraCrypt: passphrase plus optional keyfiles.
- OPAL format/wipe: OPAL admin context must be passphrase; PSID reset accepts passphrase or keyfile.

## LUKS Formatting

`_crypto_luks_format()` is the central formatter used by both `bd_crypto_luks_format()` and OPAL formatting.

Important behavior:
- Selects `CRYPT_LUKS1` or `CRYPT_LUKS2`.
- Defaults software encryption to `aes-xts-plain64` and 256-bit key size, doubling key size for XTS if user did not specify one.
- Supports optional entropy waiting through `/dev/random` and `RNDGETENTCNT`.
- Normalizes PBKDF parameters through `get_pbkdf_params()`, with special handling for PBKDF2 versus Argon-style parameters.
- Validates LUKS1 extras: only `data_alignment`, `data_device`, and PBKDF2 are valid.
- LUKS2 supports integrity, sector size, label, subsystem, data device, data alignment, and PBKDF.
- OPAL mode can call `crypt_format_luks2_opal()` and adds OPAL key size to the software key size calculation.
- Adds the initial keyslot after formatting using either passphrase data or keyfile contents.

Notable risk:
- `min_entropy` can intentionally block forever.
- OPAL behavior is compile-time conditional and has a cryptsetup workaround to initialize PBKDF state before OPAL formatting.
- Formatting with hardware-only OPAL rejects a cipher, while software+hardware can use normal cipher parameters.

## LUKS Open, Close, Resize, Suspend, Resume

`bd_crypto_luks_open_flags()` validates the dm name, loads LUKS metadata, maps libblockdev flags to cryptsetup activation flags, then activates by passphrase, keyfile-derived passphrase, or kernel keyring key. `_is_dm_name_valid()` rejects names of 128+ bytes and names containing `/`.

`bd_crypto_luks_open()` is a read-only boolean wrapper over `_flags()`.

`_crypto_close()` is shared by LUKS, integrity, TrueCrypt/VeraCrypt, BitLocker, and FileVault2 close paths. It initializes by mapper name and calls `crypt_deactivate()`.

`bd_crypto_luks_resize()` initializes by active mapper name, optionally verifies a provided passphrase/keyfile for LUKS2 devices that require a verified kernel key, and calls `crypt_resize()`. It maps the special LUKS2 permission failure to `BD_CRYPTO_ERROR_RESIZE_PERM`.

`bd_crypto_luks_suspend()` and `bd_crypto_luks_resume()` wrap `crypt_suspend()` and `crypt_resume_by_passphrase()`; resume accepts passphrase or keyfile contexts.

## LUKS Key Management

`bd_crypto_luks_add_key()` loads current and new secret material from passphrase/keyfile contexts and calls `crypt_keyslot_add_by_passphrase()`.

`bd_crypto_luks_remove_key()` first activates by the supplied secret with no mapper name to discover the matching keyslot, then destroys that slot.

`bd_crypto_luks_change_key()` calls `crypt_keyslot_change_by_passphrase()` using current and replacement secrets.

`bd_crypto_luks_kill_slot()` destroys the specified keyslot directly after loading LUKS metadata. The documentation warns it can destroy the last remaining keyslot without confirmation.

Secret buffers loaded from keyfiles are released with `crypt_safe_free()`.

## LUKS Metadata Operations

The file wraps:
- `crypt_header_backup()` and `crypt_header_restore()`
- `crypt_set_label()` for LUKS2 labels/subsystems
- `crypt_set_uuid()`
- `crypt_convert()` between LUKS1 and LUKS2
- `crypt_persistent_flags_set()` for LUKS2 persistent activation flags

`bd_crypto_luks_check_label()` enforces 47-character maximums for labels and subsystems.

Persistent flags include discards, CPU/workqueue flags, no journal, and high priority. High priority requires `LIBCRYPTSETUP_28`.

## LUKS and Crypto Queries

`bd_crypto_device_is_luks()` uses blkid safe probing with retries to require `USAGE=crypto` and `TYPE=crypto_LUKS`.

`bd_crypto_luks_status()` maps `crypt_status()` states to `"invalid"`, `"inactive"`, `"active"`, or `"busy"`.

`bd_crypto_luks_info()` can initialize either by backing block device or active mapper name. It reports version, cipher, mode, UUID, backing device, sector size, metadata size, label, subsystem, and hardware encryption type. LUKS2 label/subsystem are collected through blkid probing.

`bd_crypto_luks_token_info()` iterates available LUKS2 token IDs, skips invalid/inactive tokens, records token type, and finds the first assigned keyslot.

`bd_crypto_bitlk_info()` and `bd_crypto_integrity_info()` provide analogous query structs for BitLocker and dm-integrity.

## dm-integrity

`bd_crypto_integrity_format()` formats a device with `CRYPT_INTEGRITY`, optional extra geometry/journal parameters, optional volume-key authentication, and optional wipe. When wiping, it temporarily activates a private dm-integrity mapping, calls `crypt_wipe()` with progress mapping from 50% to 100%, then deactivates the temporary device.

`bd_crypto_integrity_open()` validates volume-key context, maps open flags to cryptsetup activation flags, handles compile-time support for recalculation reset, validates dm name, loads integrity metadata, and activates by volume key.

`bd_crypto_integrity_close()` delegates to `_crypto_close()`.

## Kernel Keyring

`bd_crypto_keyring_add_key()` stores arbitrary key data in the session keyring with key type `"user"` through `add_key()`. Failures are reported with `BD_CRYPTO_ERROR_KEYRING`.

## TrueCrypt/VeraCrypt

`bd_crypto_device_seems_encrypted()` reads the first 512 bytes, computes a chi-square statistic over byte frequencies, and treats values between fixed lower/upper limits as possible encrypted data. This is heuristic-only and documented for TCRYPT-like volumes without cleartext headers.

`bd_crypto_tc_open_flags()` supports passphrase and/or keyfile arrays, optional hidden/system headers, VeraCrypt modes, VeraCrypt PIM, read-only, and discards. It loads `CRYPT_TCRYPT` with `crypt_params_tcrypt` and activates by volume key.

`bd_crypto_tc_open()` maps the legacy `read_only` boolean to flags. `bd_crypto_tc_close()` delegates to `_crypto_close()`.

## Escrow

When compiled without `WITH_BD_ESCROW`, `bd_crypto_escrow_device()` delegates to capability gating and returns unavailable.

With escrow support:
- Initializes NSS with no DB if needed.
- Opens the LUKS volume through `volume_key`.
- Supplies the passphrase through libvolume_key UI callbacks.
- Decodes caller-supplied certificate data with NSS.
- Builds output names from sanitized volume label/UUID.
- Writes asymmetric escrow packet files, and optionally a backup-passphrase escrow packet.

Notable risk:
- Output file names are derived from label/UUID with only `/` replaced.
- The function writes binary packet data through `GIOChannel` with encoding disabled.

## BitLocker and FileVault2

`bd_crypto_bitlk_open_flags()` loads `CRYPT_BITLK`, supports passphrase or keyfile contexts, maps read-only/discard flags, and activates by passphrase.

FileVault2 paths are compiled only with libcryptsetup 2.6+. When unavailable, the functions return the same technology-unavailable error as capability checks. When available, FileVault2 open mirrors the BitLocker path with `CRYPT_FVAULT2`.

## OPAL

`bd_crypto_opal_is_supported()` either returns technology unavailable or calls Linux `IOC_OPAL_GET_STATUS` and checks OPAL support/locking flags.

`bd_crypto_opal_wipe_device()` requires an existing LUKS HW-OPAL device, verifies hardware encryption type through cryptsetup, requires passphrase context, and calls `crypt_wipe_hw_opal()` for the LUKS2 segment.

`bd_crypto_opal_format()` validates requested hardware-encryption mode, rejects software cipher for hardware-only mode, verifies OPAL support, then delegates to `_crypto_luks_format()` with LUKS2 and OPAL parameters.

`bd_crypto_opal_reset_device()` verifies OPAL support, reads PSID from passphrase or keyfile, and calls `crypt_wipe_hw_opal()` with `CRYPT_NO_SEGMENT`. The public documentation warns this removes all data.

## Dependencies

Primary dependencies:
- GLib for memory, errors, strings, arrays, random integers, regex-like utilities elsewhere, and progress logging utilities.
- libcryptsetup for all crypto/device mapping operations.
- blkid for probing LUKS labels/subsystems and LUKS detection.
- Linux random ioctl and OPAL ioctls.
- keyutils for kernel keyring.
- Optional NSS and `volume_key` for escrow.

## Notable Risks

- Many APIs are destructive or key-destructive; callers must supply their own confirmation/policy layer.
- Context-type validation is distributed across operations, so new context types require careful auditing of every operation.
- Some features are compile-time gated by cryptsetup versions, making behavior vary across builds.
- The passphrase generator uses GLib pseudo-random APIs rather than direct kernel CSPRNG use.
- dm names are only checked for length and slash characters; other dm naming edge cases are left to cryptsetup/device mapper.
- Heuristic encrypted-device detection is intentionally probabilistic and should not be treated as proof.
