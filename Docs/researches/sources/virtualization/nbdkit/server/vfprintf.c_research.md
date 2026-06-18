# File Research: sources/virtualization/nbdkit/server/vfprintf.c

This portability file provides `replace_vfprintf` when the platform `vfprintf` lacks `%m` support. It finds the first `%m` in the format string, replaces it with `strerror(errno)` using `asprintf`, calls the real `vfprintf`, frees the replacement buffer, and returns the result.

The implementation handles only the first `%m`, explicitly documenting that multiple occurrences may produce broken output. It is compiled only when `HAVE_VFPRINTF_PERCENT_M` is false, mainly for BSD-like portability.
