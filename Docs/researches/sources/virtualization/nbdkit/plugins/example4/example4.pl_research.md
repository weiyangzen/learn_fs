# File Research: sources/virtualization/nbdkit/plugins/example4/example4.pl

Example nbdkit plugin written in Perl.

Key behavior:
- Requires `size=<N>` in bytes.
- Allocates a single shared in-memory string of zero bytes in `get_ready`.
- `open` returns a small hash handle containing readonly status.
- `get_size` returns `length($disk)`.
- `pread` returns a substring.
- `pwrite` overwrites a substring.
- `dump_plugin` prints `example4_extra=hello`.

Educational focus:
- Shows the Perl plugin API and the same core lifecycle concepts as C examples in a compact scripting form.
