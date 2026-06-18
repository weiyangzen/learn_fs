# sources/test-tools/kdevops/scripts/kconfig/util.c

## Purpose
`util.c` provides small Kconfig utility functions: filename string interning and a growable string buffer (`struct gstr`) used to assemble help, relation, and generated dependency text.

## Important APIs, Types, And Functions
Exports are `file_lookup()`, `str_new()`, `str_free()`, `str_append()`, `str_printf()`, and `str_get()`. It uses `HASHTABLE_DEFINE(file_hashtable, 1U << 11)` and `struct file` entries for interned names.

## Control Flow
`file_lookup()` hashes a filename, returns an existing interned pointer if found, otherwise allocates a `struct file`, duplicates the name, adds it to the hashtable, and returns the stable pointer. `str_new()` creates an empty growable buffer. `str_append()` extends capacity in 64-byte chunks when needed and appends text. `str_printf()` formats into a temporary stack buffer then appends. `str_free()` frees the buffer contents. `str_get()` returns the current char pointer.

## State And Persistence
The file has process-global interned filename storage that is never freed during normal execution. `struct gstr` instances are caller-owned heap buffers. No disk persistence occurs.

## Dependencies And Integration Points
Depends on `hashtable.h`, `xalloc.h`, standard allocation/formatting APIs, and Kconfig `internal.h` definitions. Used by parser/autoconf dependency generation, menu help/search formatting, symbol warnings, and any code needing stable filename pointers.

## Risks And Edge Cases
`str_printf()` uses a fixed 4096-byte temporary buffer, truncating longer formatted strings. `file_lookup()` intentionally leaks interned names for process lifetime. Callers must call `str_free()` for owned `gstr` buffers.

## Test Signals
Unit-style tests can intern duplicate filenames, append many strings across capacity boundaries, format long text, free empty/non-empty buffers, and verify relation/help generation does not truncate unexpectedly.
