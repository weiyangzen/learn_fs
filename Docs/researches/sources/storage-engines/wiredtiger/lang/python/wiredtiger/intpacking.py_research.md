# sources/storage-engines/wiredtiger/lang/python/wiredtiger/intpacking.py

This module implements WiredTiger variable-length integer encoding. `pack_int(x)` emits ordered bytes for signed/unsigned values up to 64 bits, while `unpack_int(b)` returns `(value, remaining_bytes)`. Marker constants divide negative and positive values into one-byte, two-byte, and multi-byte encodings. Large values are big-endian packed and trimmed of redundant leading `0xff` or `0x00`.

The module is stateless and is used by `packing.py` for integral fields and raw-length prefixes. It depends on `struct` and byte helpers from `packutil`. Risks include lack of explicit range rejection, historical Python 2-only self-test code, and byte/string compatibility assumptions. Tests should hit every marker boundary and verify that encoded byte order matches numeric order.
