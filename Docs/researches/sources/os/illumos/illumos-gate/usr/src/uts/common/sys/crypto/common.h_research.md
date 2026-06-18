# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crypto/common.h

## Role

Defines common data structures, mechanism names, key/data representations, provider metadata, command types, and error codes for the Kernel Cryptographic Framework.

## Mechanisms

- `CRYPTO_MAX_MECH_NAME`
- `crypto_mech_name_t`
- `crypto_mech_type_t`
- `crypto_mechanism_t`
- `crypto_mechanism32_t` for 32-bit syscall compatibility.

Parameter structures include AES CTR, CCM, GCM, GMAC, and ECDH1 derive parameters, with 32-bit variants under kernel syscall compatibility.

## Mechanism Flags and Names

- Key size units:
  - `CRYPTO_KEYSIZE_UNIT_IN_BITS`
  - `CRYPTO_KEYSIZE_UNIT_IN_BYTES`
- `CRYPTO_CAN_SHARE_OPSTATE`

Mechanism name constants include MD4/MD5/SHA1/SHA2, HMAC variants, DES/3DES, Blowfish, AES CBC/CMAC/ECB/CTR/CCM/GCM/GMAC/CFB128, RC4, RSA, EC, ECDH, and ECDSA names.

## Shared Operation Context

- `arcfour_state_t`: shared RC4 operation state with architecture-specific layout.

## Data Representation

- `crypto_data_format_t`: raw, `uio`, or `mblk`.
- `crypto_data_t`: format, offset, length, misc data, and union for raw iovec, uio, or mblk.
- `crypto_dual_data_t`: adds second offset/length for dual operations.

## Key Representation

- `crypto_key_format_t`: raw, reference, or attribute list.
- `crypto_attr_type_t`
- PKCS#11-like attribute constants for RSA, DH/DSA, EC, generic secret, AES, DES.
- `crypto_object_attribute_t`
- `crypto_key_t`
- 32-bit attribute/key variants.
- Convenience macros for key union fields.
- `CRYPTO_BITS2BYTES()` and `CRYPTO_BYTES2BITS()`.

## Providers and Sessions

- Provider types: hardware, software, logical.
- `crypto_provider_id_t`, `KCF_PROVID_INVALID`.
- Provider and device list entries.
- User types: security officer and user.
- `crypto_version_t`
- Opaque session/provider handles.
- Provider extended info limits and `crypto_provider_ext_info_t`.
- `crypto_session_id_t`

## Data Command Types

- Copy from data.
- Copy to data.
- Compare to data.
- MD5/SHA1/SHA2 digest data.
- GHASH data.

Operation flags include update/final, MD5/SHA1/SHA2, sign, verify.

## Status and Error Codes

Defines `CRYPTO_SUCCESS` through `CRYPTO_FIPS140_ERROR`, with `CRYPTO_LAST_ERROR` currently matching `0x53`.

Errors cover memory, arguments, device, encrypted data, keys, mechanisms, sessions, signatures, templates, wrapping/unwrapping, users/PINs, random number generation, provider/version/busy states, permissions, weak keys, and FIPS errors.

Special values:

- `CRYPTO_UNAVAILABLE_INFO`
- `CRYPTO_EFFECTIVELY_INFINITE`

## Research Relevance

Foundational KCF ABI/types header. Any kernel crypto consumer, provider, encrypted I/O path, or crypto-adjacent filesystem integration depends on these definitions.
