# sources/object-store/minio/cmd/metacache-entries.go

## Purpose

`metacache-entries.go` defines the entry model and algorithms used to sort, filter, merge, resolve, and convert metacache listing results. It is central to turning disk-level metadata streams into S3 object and prefix listings.

## Important APIs, Control Flow, And State

`metaCacheEntry` represents either an object with metadata or a prefix directory without metadata. It can test object/dir forms, prefix membership, directory containment, latest delete markers, all-free versions, and decode metadata into `FileInfo`, `FileInfoVersions`, or cached `xlMetaV2`. `matches` compares two entries with strict or non-strict metadata rules, preferring newer modtimes or richer version sets when mismatched.

`metaCacheEntries` provides sorting, sortedness checks, shallow cloning, first-found scans, names, and quorum-based `resolve`. `resolve` counts directory and object validity, requires dir/object quorum, fast-paths complete agreement, and otherwise merges shallow xl.meta versions with `mergeXLV2Versions`, serializing the result into pooled metadata bytes. `metaCacheEntriesSorted` wraps sorted entries with list ID, reuse/pool ownership, and last skipped entry. It converts entries to object-version listings or object listings while collapsing delimiter prefixes, skipping purge-status versions, and consulting bucket versioning. It can forward/truncate by marker, merge sorted lists, filter prefixes/objects/recursive entries, and release pooled metadata when `reuse` is set.

`mergeEntryChannels` is the streaming fan-in: it merges sorted channels, handles same clean paths, discards pure directory entries when an object of the same path exists, merges versions from duplicate object entries using read quorum, emits strictly increasing names, closes output, and honors context cancellation.

State is mostly in-memory slices and optionally pooled metadata buffers. Dependencies include xl.meta decoding, metadata pools, bucket versioning, lifecycle/listing helpers, path normalization, and console/internal logging.

## Risks And Test Signals

Risks are high: quorum resolution can hide or expose versions, non-strict matching changes availability, metadata buffer reuse can leak or corrupt data if ownership is wrong, delimiter collapsing affects S3 compatibility, and corrupted metadata may be treated as delete/all-free in some paths. `metacache-entries_test.go` covers sorting, forwarding, merge ordering, filters, `isInDir`, and many `resolve` quorum/version/delete-marker cases.
