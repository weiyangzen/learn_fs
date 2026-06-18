# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crypto/elfsign.h

## Role

Defines private structures and status codes for ELF/file signature metadata exchanged among elfsign, libpkcs11, kcfd, and KCF.

## Status

- `ELFsign_status_t`:
  - unknown
  - success
  - failed
  - not signed
  - invalid cert path
  - invalid ELF object
  - unavailable

## Constants

- `SIG_MAX_LENGTH`: 1024.
- `ELF_SIGNATURE_SECTION`: `.SUNW_signature`.
- `filesig_vers_t`: 32-bit signature version type.

## Signature Layout

- `struct filesignatures`:
  - signature count.
  - padding.
  - union containing raw data, one `filesig`, or alignment field.
- `struct filesig`:
  - total signature size.
  - version.
  - version-specific payload:
    - version 1: DN size, signature size, OID size, data.
    - version 3: timestamp plus DN/signature/OID sizes and data.

Macros alias nested union fields for easier access.

## Traversal and Alignment

- `filesig_ALIGN(s)`: 64-bit alignment.
- `filesig_next(ptr)`: advances to the next signature record.

## Versions

- `FILESIG_UNKNOWN`
- `FILESIG_VERSION1`: all but signature section.
- `FILESIG_VERSION2`: version 1 format, SHF_ALLOC only.
- `FILESIG_VERSION3`: all but signature section.
- `FILESIG_VERSION4`: version 3 format, SHF_ALLOC only.

## Research Relevance

Relevant to module/file signature verification and KCF/daemon coordination around signed ELF objects.
