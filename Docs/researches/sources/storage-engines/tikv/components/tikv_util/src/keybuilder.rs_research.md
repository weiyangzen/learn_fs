# sources/storage-engines/tikv/components/tikv_util/src/keybuilder.rs

## Purpose
Implements `KeyBuilder`, a low-allocation helper for constructing byte keys when a prefix may be reserved and filled later.

## Important APIs, Types, And Functions
`KeyBuilder` owns a `Vec<u8>` and a `start` offset. Constructors are `new(max_size, reserved_prefix_len)`, `from_vec(vec, reserved_prefix_len, reserved_suffix_len)`, and `from_slice(slice, reserved_prefix_len, reserved_suffix_len)`. Mutators and views are `set_prefix`, `append`, `as_ptr`, `is_empty`, `len`, `as_slice`, and `build`.

## Control Flow
`new` reserves capacity and unsafely sets length for reserved prefix bytes. `from_vec` reuses the input vector when capacity permits by copying existing bytes forward to make prefix space; otherwise it falls back to `from_slice`. `set_prefix` asserts the reserved prefix length exactly matches the supplied prefix, copies bytes into the beginning of the buffer, and sets `start` to zero. `build` shifts visible bytes to the front if the prefix was never filled.

## State And Persistence
State is only the owned vector and visible-start offset. No persistence or sharing exists.

## Dependencies And Integration
Uses `std::ptr` for overlapping and non-overlapping byte moves. It integrates with key-encoding paths that need to prepend region/table/engine prefixes without repeated allocation.

## Risks
The implementation uses unsafe `set_len` and pointer copies. It is sound only if callers respect the reserved prefix invariant and never read uninitialized reserved bytes through `as_slice`; the `start` offset protects that until `set_prefix`. `set_prefix` panics on mismatched prefix length. `as_ptr` returns the visible start pointer and is unsafe for callers to dereference beyond `len`.

## Test Signals
The unit test covers construction through `new`, `from_vec` with and without setting the prefix, vector reuse with enough capacity, and `from_slice`, verifying final byte output and length changes.
