# sources/object-store/minio/cmd/xl-storage-format-utils_test.go

Tests metadata hashing and file-version extraction. `Test_hashDeterministicString` proves map iteration order independence and sensitivity to added/removed/changed entries. `TestGetFileInfoVersions` builds serialized `xlMetaV2` with regular and tier-free versions, then validates filtered and inclusive results plus `NumVersions`.

State is in-memory serialized metadata only. The file depends on lifecycle transition constants, UUID helpers, and `xlMetaV2` behavior.

Coverage is strong for free-version partition ordering but does not cover indexed meta input, inline data extraction, synthetic empty metadata, or byte-map hashing.
