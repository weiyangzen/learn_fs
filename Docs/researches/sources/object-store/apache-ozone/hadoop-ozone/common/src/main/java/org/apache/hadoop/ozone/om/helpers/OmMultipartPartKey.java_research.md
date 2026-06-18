# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartPartKey.java

Purpose: Typed RocksDB key for multipart part rows and prefix scans.

Important APIs/types/functions: `of(uploadId, partNumber)` creates a full key; `prefix(uploadId)` creates an iteration prefix. `getCodec` returns a custom codec supporting `CodecBuffer`. Encoding is `uploadId` UTF-8 bytes, `/`, and optional big-endian int32 part number.

Control flow and state: Decode determines whether raw bytes are a full key or prefix by checking the separator before the 4-byte suffix first, then trailing separator. This avoids misclassifying part numbers whose low byte equals `/`. Invalid/missing separators throw `CodecException`.

State and persistence behavior: Used as persisted key bytes in the multipart parts table. Prefix keys are valid only for scans, not complete row identity.

Dependencies and integration points: Integrates with HDDS DB codec APIs, `CodecBuffer`, and `StringCodec`. Used by MPU schema version 1 part storage and prefix iteration.

Risks: Upload IDs containing `/` are supported because decode uses the last separator implied by suffix length, but malformed data can still throw. Big-endian integer ordering preserves numeric ordering only for positive part numbers in normal MPU range.

Test signals: Codec round trips for prefix and full keys, part number 47 low-byte separator case, invalid empty/missing separator data, CodecBuffer path, and RocksDB prefix scan ordering.
