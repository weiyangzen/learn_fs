# sources/storage-engines/foundationdb/fdbserver/kvstore/IPager.h

## Purpose
`IPager.h` defines common pager interfaces and the `ArenaPage` physical page format used by FoundationDB storage engines such as Redwood/DWAL pager implementations. It specifies page identifiers, event classifications, page encoding/checksum behavior, snapshot reads, and the `IPager2` virtual API.

## Important APIs, Types, and Functions
The header defines page ID typedefs and sentinels, `PagerEvents`, `PagerEventReasons`, `EncodingType`, and `PageType`. `ArbitraryObject` is a type-erased ownership hook. `ArenaPage` owns aligned arena memory and implements `init`, `clone`, `getSubPage`, `setWriteInfo`, `setLogicalPageInfo`, `preWrite`, `postReadHeader`, and `postReadPayload`. `IPagerSnapshot` exposes versioned page reads. `IPager2` defines allocation, reads, writes, atomic update, free/remap, extent, snapshot, commit, storage accounting, initialization, and oldest-readable-version operations.

## Control Flow
New pages are initialized with `ArenaPage::init`, which writes `PageHeader`, selects header version 1, computes encoding-header and payload offsets, initializes forensic fields, and exposes the payload. Before disk write, callers set metadata and call `preWrite`; this writes the payload checksum or legacy XOR encoding, then updates the Redwood header checksum. After disk read, callers call `postReadHeader` to validate non-payload bytes and physical page ID, then `postReadPayload` to validate/decode the payload.

## State and Persistence Behavior
The page format is byte-packed and persistent: `PageHeader`, `RedwoodHeaderV1`, optional encoding header, then payload. XXHash64 is the current normal encoding, while deprecated encryption enum values remain reserved for compatibility and old simulation files. Runtime-only extension state is carried by `extra`.

## Dependencies and Integration Points
This header depends on FDB client types, Flow futures/errors/arena/reference counting/fast allocation, protocol versioning, encryption utilities, and XXHash. Concrete pagers implement `IPager2`; B-tree and queue code use `ArenaPage` instances as disk payload carriers. Event/reason enums feed page-cache and pager metrics.

## Risks
Persistent enum values and packed header layout are compatibility-sensitive. `ArbitraryObject::destructOnly` does not null fields by itself, so assignment/reset paths must be used carefully. Deprecated XOR support is simulation-only and requires `legacyXorWith`. Payload access before `init` or post-read calls is unsafe.

## Test Signals
`IPager.cpp` checks XXHash payload corruption detection. Additional coverage should come from concrete pager tests for commits, snapshots, remap queues, extents, old-version retention, and wrong page ID/header checksum failures.
