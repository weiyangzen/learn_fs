# sources/object-store/minio/cmd/xl-storage-meta-inline.go

## Purpose
This file implements the inline-data tail for XL metadata v2. It stores small object payloads as msgp-encoded string-to-bytes entries after the main metadata blob, allowing zero-byte/small inline object data to be persisted in `xl.meta` rather than a separate data directory.

## Important APIs, Types, and Functions
`xlMetaInlineData` is a raw byte slice with a one-byte format version followed by a msgp map of key/value pairs. `versionOK`, `afterVersion`, `validate`, `repair`, `list`, `entries`, and `find` inspect serialized inline data without a full object abstraction. Mutators `replace`, `rename`, and `remove` rebuild the serialized map with updated entries. `serialize` constructs the versioned payload. `xlMetaV2TrimData` strips the inline data tail from a serialized XL metadata buffer without unmarshalling the metadata.

## Control Flow
Read paths first accept empty data, then validate the leading version byte and read a msgp map header from the payload. Iteration uses zero-copy msgp key/value reads where possible. `find` returns the bytes for a matching key and skips other entries. `validate` fails on unknown versions, malformed msgp, or empty keys. `repair` salvages valid prefix entries into a new serialized payload, or clears the data if the version/map header is invalid.

Mutators parse the existing map, collect key/value slices, calculate an approximate payload size, and call `serialize`. `replace` updates a matching key or appends a new one. `rename` swaps a key only if found. `remove` supports multiple keys and switches to a map lookup for larger remove sets. Removing all entries clears the inline-data slice.

`xlMetaV2TrimData` checks the outer XL header/version, skips the main metadata bytes and CRC where present, computes the end offset before inline data, and returns that prefix. On parse errors it logs and returns the original buffer to avoid destructive truncation.

## State and Persistence Behavior
Inline data is stored outside the main indexed metadata CRC and is keyed by version ID or null-version ID. The current inline data format version is `1`; unknown non-empty versions are rejected or repaired away. `xlMetaV2.AddVersion` inserts data into this structure when `FileInfo.Data` is non-empty or the object size is zero. `xlMetaV2Object.InlineData` separately marks an object version as likely having inline data through internal metadata, while this file owns the actual byte map.

## Dependencies and Integration Points
The file depends on `tinylib/msgp`, `slices`, error/log helpers, and the outer XL v2 header parsing from `xl-storage-format-v2.go`. It is used by `xlMetaV2.Load`, `AppendTo`, `AddVersion`, `SharedDataDirCount`, tests, and metacache merge paths that trim data before comparing/listing metadata.

## Risks and Edge Cases
Because this code works directly on serialized bytes, size accounting and msgp prefix constants must remain correct. `repair` salvages syntactically valid entries but cannot verify payload integrity. Inline data is outside the metadata CRC, so corruption detection relies on msgp validation rather than checksum comparison. `xlMetaV2TrimData` must preserve old v1.0 metadata and handle v1.1/v1.2 variable CRC layouts correctly; otherwise list/merge paths could compare inconsistent bytes.

## Test Signals
`TestXLV2FormatData` covers inline data add/list/find/remove/replace/rename, append/load round-trip, trim behavior, and metadata corruption detection after trimming. `TestDeleteVersionWithSharedDataDir` verifies inline data versions do not count as sharing local data directories. `Test_mergeEntryChannels` trims metadata before merge, indirectly covering trim compatibility with fixture metadata.
