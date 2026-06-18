## `sources/storage-engines/rocksdb/utilities/cache_dump_load_impl.h`

Purpose: declares the concrete cache dump/load format, default dumper/loader classes, file-backed reader/writer classes, and helper encode/decode routines.

Important APIs and types: `CacheDumpUnitType` enumerates header, footer, data, filter, properties, compression dictionary, range deletion, hash index, meta/index, deprecated filter, filter metadata, and max marker values. `DumpUnitMeta` holds sequence number, checksum, and serialized unit size. `DumpUnit` holds timestamp, type, cache key, value length/checksum, and value pointer. `CacheDumperImpl` and `CacheDumpedLoaderImpl` implement public interfaces. `ToFileCacheDumpWriter` and `FromFileCacheDumpReader` implement size-prefixed stream I/O. `CacheDumperHelper` encodes and decodes metadata and units.

Control flow represented by declarations: dumpers call `WriteHeader()`, `DumpOneBlockCallBack()`, `WriteBlock()`, and `WriteFooter()`. Loaders call `ReadHeader()`, then repeated `ReadCacheBlock()`. File writer methods write a 4-byte size prefix before metadata or packet data; file reader methods maintain a running offset and read in 1 KiB chunks.

State and persistence behavior: the on-disk stream is a sequence of length-prefixed metadata and packet records. Metadata encoding is fixed 16 bytes. Dump unit encoding stores timestamp, one-byte type, length-prefixed key, fixed value length/checksum, and length-prefixed value bytes. Reader state is `offset_`, reusable buffer, and last `Slice` result.

Dependencies and integration: includes file readers/writers, public cache dump/load API, block-based table blocks/readers, filter blocks, cache key utilities, and hash containers.

Risks: `DumpUnit::value` is a raw pointer and changes ownership semantics between dumping and loading. `FromFileCacheDumpReader::Read()` appends into the destination string without clearing it, so callers must clear strings before reuse; current loader does. The reader casts requested length to `unsigned int`, which is a boundary risk for very large packets. `DecodeDumpUnit()` indexes `encoded_slice[0]` without first checking non-empty after timestamp decode.

Test signals: no direct tests in this subset; the encode/decode helpers and file reader/writer are key candidates for corruption and boundary tests.
