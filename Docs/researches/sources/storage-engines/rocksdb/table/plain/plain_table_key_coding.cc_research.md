<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_key_coding.cc -->
# sources/storage-engines/rocksdb/table/plain/plain_table_key_coding.cc

Purpose: Implements low-level key encoding, file reading, and key/value decoding for RocksDB plain table rows.

Important APIs and functions: Defines `PlainTableEntryType` values `kFullKey`, `kPrefixFromPreviousKey`, and `kKeySuffix`; local `EncodeSize()`; `PlainTableKeyDecoder::DecodeSize`; `PlainTableKeyEncoder::AppendKey`; `PlainTableFileReader::GetFromBuffer`, `ReadNonMmap`, `ReadVarint32`, `ReadVarint32NonMmap`; and decoder methods `ReadInternalKey`, `NextPlainEncodingKey`, `NextPrefixEncodingKey`, `NextKey`, and `NextKeyNoValue`.

Control flow: Encoding writes either plain keys with optional variable user-key length or prefix-compressed keys using full-key records at prefix boundaries/sparseness intervals and suffix records for later keys in the same prefix. Sequence-zero value keys omit the 8-byte trailer and append `PlainTableFactory::kValueTypeSeqId0`. Decoding mirrors this: it reads entry type/size, reconstructs full or prefix-compressed internal keys, handles the sequence-zero shortcut, then reads varint value size and value bytes. `PlainTableFileReader` returns direct mmap slices or manages two reusable non-mmap buffers with a 256-byte minimum prefetch.

State and persistence: Persistent row bytes are the encoded key, optional metadata byte, varint value size, and value bytes. Encoder state tracks previous prefix and key count within prefix. Decoder state tracks saved user key, current reconstructed key, prefix length, and encoding mode. Non-mmap reader state caches two recent buffers and last read status.

Dependencies and integration points: Used by `PlainTableBuilder` and `PlainTableReader`. Depends on internal key parsing, `WritableFileWriter`, plain table factory constants, reader file info, coding utilities, prefix extractors, and `IterKey` for reconstructed key ownership.

Risks: Prefix decoding depends on a valid prior full key and correct `prefix_len_`. Non-mmap slices are invalidated by subsequent reads unless copied, so decoder copies keys when needed. Mmap paths assert bounds. Varint EOF returns corruption. Sequence-zero shortcut must remain compatible with the persistent format.

Test signals: Fixed and variable plain encoding, prefix encoding with first/second/later keys, sparseness-triggered full keys, sequence-zero value shortcut, malformed entry type/varint EOF, mmap vs non-mmap slice lifetime, buffer cache hits/replacement, and value-size/value read boundaries.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_key_coding.cc -->
