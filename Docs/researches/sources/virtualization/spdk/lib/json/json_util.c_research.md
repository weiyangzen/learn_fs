# File Research: sources/virtualization/spdk/lib/json/json_util.c

Full-file read: 733 lines.

This file provides utility functions for working with parsed SPDK JSON token arrays.

Main responsibilities:
- Compute token span length and array element count.
- Compare and duplicate JSON string/name values as C strings.
- Split JSON numbers into sign, significand, and exponent with overflow checks.
- Convert JSON numbers to fixed integer types.
- Decode JSON objects and arrays using decoder tables.
- Free decoder-owned object fields by decoding invalid sentinel values.
- Decode booleans, strings, UUIDs, and integer types.
- Find typed object members and iterate object/array values.

Important control flow:
- `_json_decode_object` tracks duplicate fields and required/optional fields using a `seen` bitmap.
- Relaxed object decoding ignores unknown fields; strict decoding rejects them.
- `spdk_json_decode_array` walks child tokens with `spdk_json_val_len`.
- `spdk_json_next` skips nested arrays/objects by walking to the matching end token.

Integration points:
- Used by RPC handlers throughout SPDK, including `iscsi_rpc.c`.
- Depends on `json_parse.c` token shapes and `spdk_uuid_parse`.

Risks and review notes:
- `spdk_json_decode_string` frees the destination pointer before replacing it; callers often preload defaults and rely on this behavior.
- `spdk_json_decode_array` requires caller-provided output storage and max size.
- Number conversion rejects exponents/fractions for integer outputs, as expected.

Testing focus:
- Duplicate/missing/unknown object keys in strict and relaxed modes.
- Numeric overflow, negative unsigned values, and fractional integers.
- Iterator behavior over nested containers.
