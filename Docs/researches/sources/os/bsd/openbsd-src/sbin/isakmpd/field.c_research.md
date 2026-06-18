# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/field.c

Runtime helper for generated packet field descriptors. It decodes, logs, reads, and writes fixed-size protocol fields described by `struct field`.

Key functions:
- `field_dump_field()` and `field_dump_payload()` pretty-print decoded fields for debug logs.
- `field_get_num()` reads 1, 2, or 4 byte network-order numeric fields.
- `field_set_num()` writes 1, 2, or 4 byte numeric fields using protocol endian helpers.
- `field_get_raw()` and `field_set_raw()` copy raw fixed-length fields.
- Static debug decoders support raw hex, decimal number, bitmask names, ignored fields, and constants.

Implementation details:
- `decode_field[]` must match the enum order in `struct field`.
- Constant and mask decoding use `struct constant_map` lookup helpers.
- Unsupported numeric lengths return failure or zero.
