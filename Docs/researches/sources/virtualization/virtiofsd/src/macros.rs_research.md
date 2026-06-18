# File Research: sources/virtualization/virtiofsd/src/macros.rs

## Scope

Small macro helper for enum-to-integer protocol values.

## API

- `enum_value!` defines a `#[repr(T)]` enum and implements `TryFrom<T>` by matching each declared variant’s numeric value.

## Role

Used by `fuse.rs` to define `Opcode` with exact FUSE request numbers while getting fallible conversion from raw wire opcode values.

## Invariants

Unknown integer values convert to `Err(())`, allowing protocol parsing to reject unsupported opcodes.
