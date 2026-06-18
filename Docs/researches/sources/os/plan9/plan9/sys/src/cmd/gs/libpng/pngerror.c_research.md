# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngerror.c

## Role

`pngerror.c` implements libpng’s error and warning handling. It defines `PNG_INTERNAL` before including `png.h`, so it can access internal `png_struct` fields and flags.

Despite the file comment saying “stub functions for i/o and memory allocation,” this file specifically centralizes fatal error dispatch, non-fatal warning dispatch, chunk-prefixed message formatting, default stderr reporting, setjmp/longjmp escape behavior, and error callback registration.

## Main Functions

`png_error(png_structp png_ptr, png_const_charp error_message)` handles fatal errors.

Its behavior is:

- Optionally strips libpng error numbers and/or text when `PNG_ERROR_NUMBERS_SUPPORTED` is enabled and `png_ptr->flags` contains `PNG_FLAG_STRIP_ERROR_NUMBERS` or `PNG_FLAG_STRIP_ERROR_TEXT`.
- Calls the user-supplied `png_ptr->error_fn` if present.
- Falls back to `png_default_error()` if no custom handler exists or if the custom handler returns.
- The default handler is expected not to return.

`png_warning(png_structp png_ptr, png_const_charp warning_message)` handles non-fatal warnings.

Its behavior is:

- Optionally skips a leading `#nnn ` warning number.
- Calls `png_ptr->warning_fn` if present.
- Otherwise calls `png_default_warning()`.

`png_chunk_error()` and `png_chunk_warning()` prepend the current chunk name from `png_ptr->chunk_name` before dispatching to the normal fatal/non-fatal handlers.

`png_set_error_fn()` installs user error and warning callbacks plus an opaque `error_ptr`.

`png_get_error_ptr()` returns that opaque pointer.

`png_set_strip_error_numbers()` is compiled when `PNG_ERROR_NUMBERS_SUPPORTED` is enabled and is intended to update strip-mode flags on `png_ptr`.

## Chunk Message Formatting

The private helper `png_format_buffer()` builds chunk-prefixed messages.

It reads four bytes from `png_ptr->chunk_name`. Alphabetic bytes are copied directly. Non-alphabetic bytes are encoded as hex in bracket form, using the local `png_digit` table. It then appends `": "` and up to 63 bytes of the supplied message via `png_strncpy`, forcing a terminator at `buffer[iout+63]`.

The local `isnonalpha(c)` macro treats ASCII `A-Z` and `a-z` as valid chunk-name characters.

This protects diagnostics from raw binary chunk-name bytes while preserving useful chunk context.

## Default Fatal Error Path

`png_default_error()` prints to `stderr` unless `PNG_NO_CONSOLE_IO` is defined.

If error-number support is enabled and the message begins with `#`, it attempts to parse a numeric prefix and prints either:

- `libpng error no. <number>: <message>`
- or a fallback malformed-prefix message.

Otherwise it prints:

- `libpng error: <message>`

For control flow:

- If `PNG_SETJMP_SUPPORTED` is enabled, it calls `longjmp(png_ptr->jmpbuf, 1)`.
- If `USE_FAR_KEYWORD` is enabled, it copies the jump buffer first, then longjmps through the copy.
- If setjmp support is disabled, it calls `PNG_ABORT()` when `png_ptr` is non-null.

Because libpng’s public pattern relies on callers setting `setjmp(png_jmpbuf(png_ptr))`, a fatal error normally unwinds back to application code rather than returning through the failed libpng call.

## Default Warning Path

`png_default_warning()` prints to `stderr` unless `PNG_NO_CONSOLE_IO` is defined.

With error-number support, it parses leading `#nnn ` warning prefixes similarly to fatal errors and prints a numbered warning when possible. Otherwise it prints a normal warning line.

Warnings return to the caller; they do not longjmp.

## Callback Contract

The file’s comments emphasize that replacement fatal error functions must not return. A custom error handler is expected to perform a longjmp or equivalent non-local exit. If it returns, `png_error()` intentionally invokes the default fatal handler afterward.

Replacement warning functions may return normally and may ignore messages.

## Notable Edge Case

`png_set_strip_error_numbers()` uses:

`png_ptr->flags &= ((~(PNG_FLAG_STRIP_ERROR_NUMBERS|PNG_FLAG_STRIP_ERROR_TEXT))&strip_mode);`

This expression clears flags through an AND operation rather than the more typical “clear then OR selected strip flags” pattern. As written, it can only preserve bits already present in both the inverted mask and `strip_mode`; it does not appear to set strip flags. This may be inherited upstream behavior or a bug in this bundled libpng version, but it is worth noting if diagnostics stripping is expected to work.

## Research Notes

This file has no filesystem behavior. Its main relevance to the broader source tree is failure control flow: libpng decode/encode errors can escape via `longjmp`, so callers in Ghostscript must establish the expected setjmp recovery path before invoking libpng operations.
