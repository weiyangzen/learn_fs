# File Research: sources/virtualization/nbdkit/plugins/example2/Makefile.am

Build definition for example2, selecting POSIX or Windows source.

Key contents:
- Builds `nbdkit-example2-plugin.la`.
- Uses `example2.c` on non-Windows and `winexample2.c` on Windows.
- Includes nbdkit headers.
- Links optional Windows import library.
- Generates POD documentation when available.
