# File Research: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngerror.c

Implements libpng 1.2.8 error and warning dispatch. It provides the public `png_error`, `png_warning`, chunk-prefixed variants, default stderr/longjmp behavior, and registration/accessor functions for application-provided error handlers.

Key elements:
- Defines `PNG_INTERNAL` before including `png.h`, enabling private struct fields, internal flags, and private prototypes.
- Declares private defaults:
  - `png_default_error`
  - `png_default_warning`
- `png_error(png_ptr, error_message)` handles fatal errors:
  - optionally strips numeric prefixes and/or error text when `PNG_ERROR_NUMBERS_SUPPORTED` and strip flags are set
  - calls `png_ptr->error_fn` when provided
  - always falls back to `png_default_error` if the custom handler is absent or returns
- `png_warning(png_ptr, warning_message)` handles non-fatal warnings:
  - strips numeric prefixes when configured
  - calls `png_ptr->warning_fn` when provided
  - otherwise calls `png_default_warning`
- `png_format_buffer` prefixes diagnostics with the current `png_ptr->chunk_name`, escaping non-alphabetic chunk-name bytes as bracketed hex pairs and limiting appended message text.
- `png_chunk_error` and `png_chunk_warning` build chunk-prefixed messages and dispatch through `png_error`/`png_warning`.
- `png_default_error`:
  - prints to `stderr` unless `PNG_NO_CONSOLE_IO`
  - supports formatted numbered errors when `PNG_ERROR_NUMBERS_SUPPORTED`
  - calls `longjmp(png_ptr->jmpbuf, 1)` when setjmp support is enabled
  - otherwise calls `PNG_ABORT()` if `png_ptr` is present
- `png_default_warning` prints warning messages to `stderr` unless console I/O is disabled.
- `png_set_error_fn` stores application error pointer, fatal error callback, and warning callback in `png_struct`.
- `png_get_error_ptr` returns the stored application error pointer.
- `png_set_strip_error_numbers` exists when `PNG_ERROR_NUMBERS_SUPPORTED` is enabled and is intended to configure stripping of numbered error metadata.

Dependencies:
- Includes `png.h` with `PNG_INTERNAL`.
- Uses `png_struct` fields from `png.h`: `flags`, `error_fn`, `warning_fn`, `error_ptr`, `chunk_name`, and `jmpbuf`.
- Uses macros and functions from `pngconf.h`: `PNGAPI`, `PNGARG`, `PNG_CONST`, `png_strncpy`, `png_memcpy`, `png_sizeof`, `PNG_ABORT`, and `PNG_SETJMP_SUPPORTED`.
- Uses `fprintf(stderr, ...)` unless console I/O is disabled.
- Uses `longjmp` through setjmp support unless setjmp is disabled.

Research notes:
- Fatal error callbacks must not return. If they do return, libpng intentionally invokes the default fatal handler, which exits via longjmp or abort.
- `png_format_buffer` assumes `png_ptr` and its `chunk_name` are valid; callers use it for current-chunk diagnostics.
- Default warning behavior is non-fatal and only logs when console I/O is enabled.
- Potential defect: `png_set_strip_error_numbers` masks `png_ptr->flags` with `((~strip_flags) & strip_mode)`, which can clear unrelated flags and does not straightforwardly set the requested strip flags. This is worth checking before relying on that API in this vendored copy.
- Error handling depends on the application setting a valid setjmp target before libpng calls that may fail; otherwise the default fatal path may jump into uninitialized state or abort depending on build configuration.
