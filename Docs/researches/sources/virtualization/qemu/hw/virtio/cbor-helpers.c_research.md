# File Research: sources/virtualization/qemu/hw/virtio/cbor-helpers.c

Helper layer around libcbor for QEMU virtio code, used to construct CBOR maps and arrays with consistent ownership cleanup. It is gated by virtio Kconfig users such as `VIRTIO_NSM`.

Key responsibilities:
- Add key/value pairs to CBOR maps using `cbor_move()` while restoring references on failure.
- Push values to CBOR arrays with equivalent ownership handling.
- Provide typed convenience helpers for adding booleans, uint8 values, uint64 values, strings, nulls, byte strings, nested maps, uint8 arrays, and uint8-keyed byte strings to maps.
- Clean up partially constructed CBOR items on allocation or insertion failure.

Important functions:
- `qemu_cbor_map_add()`: moves key/value into a `struct cbor_pair` and calls `cbor_map_add()`.
- `qemu_cbor_array_push()`: moves an item into an array.
- `qemu_cbor_add_bool_to_map()`, `qemu_cbor_add_uint8_to_map()`, `qemu_cbor_add_uint64_to_map()`: scalar helpers.
- `qemu_cbor_add_map_to_map()`: creates a definite nested map and returns it to the caller through `nested_map`.
- `qemu_cbor_add_bytestring_to_map()` and `qemu_cbor_add_uint8_key_bytestring_to_map()`: byte-string helpers.
- `qemu_cbor_add_string_to_map()` and `qemu_cbor_add_null_to_map()`: string/null helpers.
- `qemu_cbor_add_uint8_array_to_map()`: builds a definite array and pushes per-byte CBOR uint8 items.

Notable constraints:
- All helpers return `bool` success/failure and avoid propagating `Error **`.
- On successful map/array insertion, ownership is transferred to the CBOR container.
- On failure, locally held CBOR items are decref’d to avoid leaks.
