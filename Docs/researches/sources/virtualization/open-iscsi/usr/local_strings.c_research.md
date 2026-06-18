# File Research: sources/virtualization/open-iscsi/usr/local_strings.c

## Purpose
`local_strings.c` implements a simple growable string/data buffer abstraction used by older open-iscsi code.

## APIs
- `str_init_buffer()` zeroes a `str_buffer` and optionally allocates an initial zeroed buffer.
- `str_alloc_buffer()` allocates a `str_buffer` struct and initializes it.
- `str_free_buffer()` frees the internal buffer and resets lengths, but does not free the struct itself.
- `str_enlarge_data()` increases `data_length` by a signed length and reallocates the backing buffer to match when needed, zeroing newly allocated space.
- `str_remove_initial()` removes a prefix by `memmove()`, clamps negative remaining length to zero, updates length, and writes a trailing NUL.
- `str_truncate_buffer()` shrinks data length or extends it within allocated capacity by zero-filling; it logs an error if requested length exceeds allocation.
- `str_buffer_data()`, `str_data_length()`, and `str_unused_length()` are accessors.

## Integration Notes
The abstraction tracks `allocated_length`, `data_length` excluding trailing NUL, and `buffer`. It includes `log.h` for debug/error reporting.

## Risk Notes
- `str_enlarge_data()` mutates `data_length` before allocation succeeds; on `realloc()` failure, the length has already been increased even though allocation did not grow.
- `str_remove_initial()` assumes `s->buffer` is valid when `s` and `length` are nonzero.
- `str_free_buffer()` does not free a buffer object allocated by `str_alloc_buffer()`, so callers need a separate `free(s)` if they own the struct allocation.
