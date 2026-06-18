# File Research: sources/virtualization/spdk/lib/util/file.c

This file implements whole-file loading and sysfs attribute readers.

`spdk_posix_file_load()` reads a `FILE *` into a reallocating heap buffer, starting at 128 KiB and doubling up to 1 GiB. It returns the buffer and sets the final byte count on EOF, or frees and returns null on allocation/read error or if the file exceeds the growth cap.

`spdk_posix_file_load_from_name()` opens a file by name, delegates to `spdk_posix_file_load()`, closes the file, and returns the allocated contents.

`read_sysfs_attribute()` formats a path with `spdk_vsprintf_alloc()`, opens it, reads one line with `getline()`, strips a trailing newline, and returns the allocated string through `attribute_p`. `spdk_read_sysfs_attribute()` is the varargs wrapper. `spdk_read_sysfs_attribute_uint32()` reads a string attribute, parses it with `spdk_strtoll()`, checks the value is in `uint32_t` range, and returns the integer.

Memory ownership is caller-facing: successful file loads and sysfs reads return heap buffers that callers must free. Errors are negative errno where possible.
