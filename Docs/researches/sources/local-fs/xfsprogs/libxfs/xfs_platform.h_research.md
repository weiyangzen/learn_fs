# File Research: sources/local-fs/xfsprogs/libxfs/xfs_platform.h

## Role

This header is the userspace compatibility layer that lets selected XFS kernel code compile inside xfsprogs `libxfs`. It maps kernel APIs, types, feature config, logging, allocation, locking, quota, buffer, stats, and helper functions onto userspace equivalents or stubs.

## Platform Setup

The header defines userspace build context and includes:

- API renaming definitions
- platform definitions
- XFS base headers
- list/hlist/cache/bitops/kmem/atomic/spinlock shims
- radix tree, bitmask, div64, utility helpers
- types and architecture headers
- CRC and buffer IO support

It enables XFS realtime and in-memory btree config macros for `IS_ENABLED`-style code.

## Kernel API Shims

Important shims include:

- `ASSERT` mapped to `assert`
- XFS logging macros mapped to `cmn_err`
- corruption/error reporting macros
- no-op shutdown, delayed allocation, readahead, locking, stats, and tag helpers
- userspace dev_t identity conversion
- inode version accessors
- owner initialization prototype
- min/max/swap/rounding helpers
- bitmap declarations and next-bit search helpers
- power-of-two helpers
- buffer state/type helpers
- transaction buffer type helpers
- extent busy stubs
- filestream and realtime allocation stubs where unsupported
- quota reservation and dquot attach stubs
- UUID mapping
- superblock counter update macros backed by `libxfs_mod_incore_sb`

## Exposed Prototypes

The file declares functions from local libxfs components that kernel code expects but may not have explicit shared headers for, including transaction setup, transaction item handling, buffer item handling, inode item init, mount common setup, bmap helpers, verifier reporting, zeroing extents, log helpers, inode allocation setup, and other compatibility entry points.

## Notable Behavior

- Locking macros are mostly no-ops in userspace, so callers rely on higher-level tool serialization.
- Statistics macros suppress unused variable warnings.
- Some kernel-only paths are intentionally stubbed with fixed return values, such as filestream selection and realtime allocator helper in this context.
- `xfs_buf_incore` always reports not found.
- Parent or log recovery behavior that depends on kernel background state must be provided elsewhere or remains a stub.

## Dependencies

This file sits at the bottom of almost every libxfs source file. It is included by kernel-derived XFS code before normal XFS headers to provide the userspace build environment.

## Research Notes

This compatibility layer is central to xfsprogs kernel-code sharing. Changes here can silently alter semantics across large parts of libxfs, especially because many synchronization, quota, stats, and kernel background mechanisms are reduced to no-ops or simplified userspace equivalents.
