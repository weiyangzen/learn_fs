# File Research: sources/os/linux/linux/io_uring/openclose.h

Header for io_uring open, close, pipe, and fixed-fd install operations.

Key responsibilities:
- Declares prep/issue/cleanup entry points for openat/openat2.
- Declares fixed-file close helper `__io_close_fixed()`.
- Declares normal close, pipe, and fixed-fd installation handlers.
- Includes `bpf_filter.h` so openat BPF population can expose parsed open fields.

Important invariants:
- Cleanup is required for open requests that captured delayed filenames.
- `__io_close_fixed()` expects a zero-based fixed slot offset, while SQE `file_index` users are one-based except allocation sentinel cases.
