# File Research: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngrio.c

## Role

`pngrio.c` implements libpng’s read I/O abstraction. It provides the internal read dispatcher, default stdio-based reading, and the public hook for applications to install custom input callbacks.

## Main APIs and Behavior

- `png_read_data()` is the internal read entry point. It calls `png_ptr->read_data_fn` and raises `png_error()` if no read function is installed.
- `png_default_read_data()` is compiled when stdio support is present:
  - Uses `fread()` for normal platforms.
  - Uses `ReadFile()` on `_WIN32_WCE`.
  - Has a `USE_FAR_KEYWORD` variant that stages reads through a near buffer for old memory models.
- `png_set_read_fn()` installs a caller-provided `io_ptr` and read callback.
  - If stdio is enabled and `read_data_fn` is `NULL`, it installs `png_default_read_data`.
  - If stdio is disabled, it accepts the supplied callback directly.
  - It clears any write callback because a single `png_struct` cannot be both read and write configured.
  - It clears the flush callback when write flushing support exists.

## Dependencies

- `png.h` internal declarations.
- C stdio unless `PNG_NO_STDIO` is defined.
- Windows CE `ReadFile()` under `_WIN32_WCE`.
- libpng error/warning helpers.

## State Mutated

- `png_ptr->io_ptr`.
- `png_ptr->read_data_fn`.
- `png_ptr->write_data_fn` cleared when conflicting.
- `png_ptr->output_flush_fn` cleared when applicable.

## Risks and Maintenance Notes

- The default reader treats short reads as fatal `png_error("Read Error")`.
- Custom read callbacks must exactly fill the requested length or report errors through `png_error()`.
- `png_read_data()` can be called with small lengths, so unbuffered custom readers may perform poorly unless they add buffering.
- The file deliberately keeps I/O policy isolated from parsing logic in `pngread.c` and `pngpread.c`.

## Research Summary

This is a small but central indirection layer. All sequential parsing ultimately reads through this callback path, while progressive mode installs `png_push_fill_buffer()` as a synthetic read function.
