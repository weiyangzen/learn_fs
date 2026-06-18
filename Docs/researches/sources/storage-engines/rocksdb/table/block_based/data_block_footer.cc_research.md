## sources/storage-engines/rocksdb/table/block_based/data_block_footer.cc

Purpose: implements encoding and decoding of `DataBlockFooter`, the compact trailer for data block metadata. The footer packs restart count with feature bits for hash index, uniform keys, and separated KV storage.

Important APIs/functions: `DataBlockFooter::EncodeTo()` appends an optional values-section offset followed by a packed fixed32 word. `DecodeFrom()` reads from the end of a `Slice`, sets `index_type`, `separated_kv`, `is_uniform`, `num_restarts`, and optionally `values_section_offset`, then removes consumed bytes from the input.

Control flow: encode asserts restart count fits the low 28 bits, writes `values_section_offset` first when separated KV is enabled, sets bit 31 for `kDataBlockBinaryAndHash`, bit 28 for separated KV, and bit 29 for uniform keys, then writes the packed word. Decode requires at least four bytes, reads the packed word from the end, peels off known bits, rejects any remaining value above `kMaxNumRestarts`, removes the packed word, and if separated KV is set reads/removes the preceding offset.

State and persistence behavior: this is persisted block-format metadata. It changes how readers find restart arrays, separated values, hash indexes, and auto/interpolation search hints. Unknown reserved bits are treated as corruption for forward-compatibility failure rather than silent misread.

Dependencies/integration points: uses fixed32 coding utilities and `BlockBasedTableOptions::DataBlockIndexType`. `BlockBuilder::Finish()` writes this footer; `Block` parsing consumes it. `block_test.cc` directly inspects packed bits and footer size in separated/non-separated corruption tests.

Risks: bit 30 is documented as dangerous because older corruption checks can overflow; future feature allocation needs a format-version bump or careful compatibility. Decode consumes from the end, so callers must pass the full remaining block slice.

Test signals: separated KV tests, hash index tests, uniformity tests, and corruption-boundary tests in `block_test.cc` indirectly and directly validate encoding layout.
