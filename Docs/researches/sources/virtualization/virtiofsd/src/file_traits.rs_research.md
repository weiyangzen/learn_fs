# File Research: sources/virtualization/virtiofsd/src/file_traits.rs

## Scope

Traits for file sizing and volatile vectored I/O against `std::fs::File`.

## APIs Covered

- `FileSetLen`, implemented by `File`, wraps `set_len()` / `ftruncate`-style behavior.
- `FileReadWriteAtVolatile<B>` defines `read_vectored_at_volatile()` and `write_vectored_at_volatile()`.
- Blanket reference implementation delegates through `&T`.
- `volatile_impl!(File)` implements volatile vectored I/O for `File`.

## Behavior

- Converts `VolatileSlice` arrays into `libc::iovec` arrays.
- Uses `oslib::readv_at()` / `oslib::writev_at()` with optional per-call flags.
- Maintains pointer guards while syscalls operate, preserving guest-memory pointer validity.
- Marks dirty bitmap ranges for bytes read into guest memory.

## Risks And Invariants

- Offset conversion uses `try_into().unwrap()`, so callers must pass offsets representable as syscall offsets.
- Correct dirty bitmap marking matters for migration/shared memory tracking.
- Safety relies on `VolatileSlice` bounds and pointer guards staying alive for the syscall duration.
