# sources/object-store/minio/cmd/xl-storage-format-v2-legacy.go

Backward compatibility decoder for older xl.meta v2 encodings. Header dispatch handles version 1, version 2, current header version, and rejects unknown versions. Version 1 decodes a never-released four-field array; header v2 decodes the pre-EcN/EcM five-field array.

`xlMetaV2Version.unmarshalV` rejects newer metadata versions, clears stale `ObjectV2.PartIndices`, decodes current msgp format, normalizes pre-v2 delete-marker replication timestamps to UTC, and drops all-empty part ETags.

This code reads persisted legacy metadata and depends on current xl.meta v2 structs, msgp, replication metadata keys, and time parsing. Risks include backward compatibility loss, timestamp normalization side effects, and stale slice contents. No direct tests in this subset target these branches.
