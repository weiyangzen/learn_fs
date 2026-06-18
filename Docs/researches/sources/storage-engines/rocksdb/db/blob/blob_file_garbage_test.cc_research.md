# sources/storage-engines/rocksdb/db/blob/blob_file_garbage_test.cc

## Purpose
Tests serialization compatibility and corruption handling for `BlobFileGarbage`.

## Important Test Flow
`TestEncodeDecode` round-trips a record and verifies equality. `Empty` checks invalid default file number and zero garbage counts. `NonEmpty` validates explicit file number/count/bytes. `DecodeErrors` builds a truncated payload step by step and expects corruption messages for missing blob file number, garbage count, garbage bytes, custom field tag, and custom field value. `ForwardCompatibleCustomField` injects an unknown compatible tag and expects successful decode. `ForwardIncompatibleCustomField` injects a masked tag and expects corruption.

## Dependencies, Risks, and Test Signals
The tests use coding helpers and sync points. They strongly cover manifest extension behavior. Remaining risks are semantic validation of garbage values against blob-file totals and trailing bytes after end marker, which are outside this record-level test.
