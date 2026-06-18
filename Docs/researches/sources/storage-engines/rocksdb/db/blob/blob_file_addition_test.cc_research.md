# sources/storage-engines/rocksdb/db/blob/blob_file_addition_test.cc

## Purpose
Tests binary compatibility and error handling for `BlobFileAddition`.

## Important Test Flow
`TestEncodeDecode` round-trips an addition and compares equality. `Empty` checks default sentinel and zero counts. `NonEmpty` validates explicit fields including checksum bytes. `DecodeErrors` incrementally appends fields to a string and verifies corruption messages for missing blob file number, total count, total bytes, checksum method, checksum value, custom field tag, and custom field value. `ForwardCompatibleCustomField` injects an unknown compatible tag through sync point and expects decode success. `ForwardIncompatibleCustomField` injects a masked tag and expects corruption.

## Dependencies, Risks, and Test Signals
The tests depend on coding utilities and sync points. They are a strong signal for persisted manifest compatibility, especially around extension tags. Remaining risk is that they do not test extra trailing bytes after the end marker or constructor assertion behavior in release builds.
