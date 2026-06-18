# sources/storage-engines/wiredtiger/tools/py_common/decode_opts.py

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/py_common/decode_opts.py -->
## sources/storage-engines/wiredtiger/tools/py_common/decode_opts.py

### Purpose
`decode_opts.py` defines a shared dataclass for options used by WiredTiger binary/page decode tools.

### Important APIs, Types, and Functions
`DecodeOptions` groups input-routing flags (`dumpin`, `disagg_table`, `fragment`), decode behavior (`disagg`, `skip_data`, `cont`), output formatting (`split`, `bson`, `output`), seek/page limits (`offset`, `pages`), and disaggregated-storage filters/secrets (`keyfile`, `lsn`, `page_id`).

### Control Flow
There is no behavior beyond dataclass construction with defaults.

### State and Persistence
Instances are in-memory option carriers. `output` can hold a writable file-like object owned by the caller, but this module does not write to it directly.

### Dependencies and Integration Points
Depends on `dataclasses`, `typing.Any`, and `typing.Optional`. It is intended for command-line decode tools that need a consistent option object passed into page/file decoding code.

### Risks and Test Signals
The loose `Any` type for `output` keeps the dataclass flexible but defers validation to users. Tests should instantiate defaults, override every field, and verify downstream decoders interpret `pages=0` as unlimited and optional filters as `None`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/py_common/decode_opts.py -->
