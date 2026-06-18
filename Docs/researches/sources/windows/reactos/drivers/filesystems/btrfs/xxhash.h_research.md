# File Research: sources/windows/reactos/drivers/filesystems/btrfs/xxhash.h

## Purpose

Public xxHash 0.6.2 header used by the Btrfs driver for fast non-cryptographic hashing. It declares the one-shot and streaming XXH32/XXH64 APIs, canonical big-endian hash representations, optional namespacing, and static-link/private inclusion support.

## Main Components

- Version macros: `XXH_VERSION_MAJOR`, `XXH_VERSION_MINOR`, `XXH_VERSION_RELEASE`, `XXH_VERSION_NUMBER`.
- API export/private controls: `XXH_PRIVATE_API`, `XXH_STATIC_LINKING_ONLY`, `XXH_PUBLIC_API`.
- Optional symbol prefixing through `XXH_NAMESPACE`.
- Hash types:
  - `XXH32_hash_t`
  - `XXH64_hash_t`
  - `XXH_errorcode`
- One-shot functions:
  - `XXH32`
  - `XXH64`
- Streaming state APIs:
  - `XXH32_createState`, `XXH32_freeState`, `XXH32_reset`, `XXH32_update`, `XXH32_digest`
  - `XXH64_createState`, `XXH64_freeState`, `XXH64_reset`, `XXH64_update`, `XXH64_digest`
  - `XXH32_copyState`, `XXH64_copyState`
- Canonical conversion APIs:
  - `XXH32_canonicalFromHash`, `XXH64_canonicalFromHash`
  - `XXH32_hashFromCanonical`, `XXH64_hashFromCanonical`
- Static-link-only state layouts for `XXH32_state_s` and `XXH64_state_s`.

## Dependencies and Consumers

- Includes only `<stddef.h>` in the public section.
- Includes `xxhash.c` when `XXH_PRIVATE_API` is defined.
- Included by ReactOS Btrfs files such as `btrfs.c`, `read.c`, `flushthread.c`, and `calcthread.c`.
- Used by the Btrfs checksum/calculation thread path for `calc_thread_xxhash`.

## Research Notes

- This file is API surface, not implementation.
- Static state layouts are explicitly unstable and only safe for static linking.
- Canonical representation is big-endian, intended for portable persisted hash values.
- Any signature or namespace change must stay consistent with `xxhash.c` and call sites in Btrfs checksum logic.
