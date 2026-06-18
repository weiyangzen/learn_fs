# sources/storage-engines/wiredtiger/tools/py_common/binary_data.py

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/py_common/binary_data.py -->
## sources/storage-engines/wiredtiger/tools/py_common/binary_data.py

### Purpose
`binary_data.py` provides primitive binary decoding helpers used by WiredTiger file-format tools: packed integer decoding, 4-bit array decoding, escaped-hex decoding, file-as-array access, little-endian reads, and display formatting.

### Important APIs, Types, and Functions
`get_bits`, `get_int`, and `unpack_int` implement WiredTiger variable-length integer decoding. `unpack_4b_array` decodes compact small-integer arrays used by disaggregated address cookies. `decode_esc_hex` reverses WiredTiger escaped hex output. `FileAsArray` adapts a file-like stream to indexed/sliced byte access for `unpack_int`. `BinaryFile` wraps a file object with saved-byte tracking and typed reads (`read_uint8/16/32/64`, `read_packed_uint64`, `read_long_length`, `seek`, `tell`, `saved_bytes`). `ts`, `txn`, and `d_and_h` format values.

### Control Flow
Packed integer decoding branches on marker byte ranges matching WiredTiger's signed/unsigned encoding. `BinaryFile.read_packed_uint64` constructs a `FileAsArray` over itself; byte indexing causes sequential reads and updates stream position. `saved_bytes` returns bytes accumulated since the previous call and clears the accumulator.

### State and Persistence
`BinaryFile` maintains in-memory stream position through the wrapped file and a `saved` bytearray for split/raw output. `FileAsArray` tracks logical position and slice offset. No disk state is written.

### Dependencies and Integration Points
Used by `btree_format.py` and likely other decode tools. It depends only on Python typing and file-like objects.

### Risks and Test Signals
`FileAsArray.__getitem__` rejects slices only when both `stop` and `step` are non-None; stricter slice validation may be intended. It assumes reads return at least one byte before indexing `[0]`, so truncated data can raise `IndexError`. `unpack_int` needs bounds checks for short buffers. Tests should cover every marker range, truncated packed integers, `read_long_length`, `saved_bytes` after seek, escaped hex errors, and 4-bit array incomplete/excess cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/py_common/binary_data.py -->
