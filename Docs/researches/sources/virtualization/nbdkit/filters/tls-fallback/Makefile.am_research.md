# File Research: sources/virtualization/nbdkit/filters/tls-fallback/Makefile.am

This Automake file builds `nbdkit-tls-fallback-filter.la` from `tls-fallback.c` and the public filter header. It uses public/generated/common include paths, standard module flags, and the optional filter linker script.

The filter has minimal dependencies compared with most other modules: it links only the Windows import library variable and does not link common utility or replacement libraries. `nbdkit-tls-fallback-filter.pod` is distributed, and POD-enabled builds generate the man page and HTML documentation.

The build file does not conditionally disable the filter by platform or TLS library; runtime behavior is implemented through nbdkit's `is_tls` callback arguments.
