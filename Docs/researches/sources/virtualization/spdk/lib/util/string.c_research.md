# File Research: sources/virtualization/spdk/lib/util/string.c

This file contains SPDK string allocation, parsing, trimming, numeric conversion, and string-array helpers.

Formatted allocation helpers include `spdk_vsprintf_append_realloc()`, `spdk_sprintf_append_realloc()`, `spdk_vsprintf_alloc()`, and `spdk_sprintf_alloc()`. They use `vsnprintf(NULL, 0, ...)` to size output, reallocate the existing buffer when appending, and return null on formatting or allocation failure.

Basic string utilities include `spdk_strlwr()` for in-place lowercase, `spdk_str_trim()` for in-place leading/trailing whitespace removal, `spdk_str_chomp()` for removing trailing CR/LF, `spdk_strcpy_pad()` and `spdk_strlen_pad()` for fixed-size padded strings, and `spdk_mem_all_zero()` for byte-wise zero testing.

`spdk_strsepq()` is a quoted tokenizer. It splits on delimiter characters while honoring single quotes, double quotes, and backslash escapes, removes quote characters, compacts escaped characters in place, skips trailing delimiters, and advances `stringp`.

`spdk_parse_ip_addr()` destructively parses either `host:port` IPv4-style strings or `[ipv6]:port` strings, replacing separators with null bytes and returning host and optional port pointers.

`spdk_strerror_r()` handles GNU and POSIX `strerror_r()` variants and formats `Unknown error N` on failure. `spdk_parse_capacity()` parses unsigned integer capacities with optional binary suffix K/M/G and reports whether a suffix was present.

`spdk_strtol()` and `spdk_strtoll()` wrap libc conversions but reject trailing non-integer characters, overflow, other errno failures, and negative values. They return negative errno-style values on invalid input, so callers cannot parse negative numbers through these helpers.

String-array helpers allocate, duplicate, and free null-terminated `char **` arrays. `spdk_strarray_from_string()` splits on any delimiter character using `strpbrk()` and preserves empty fields between adjacent delimiters. `spdk_strarray_dup()` deep-copies a null-terminated string array. `spdk_strarray_free()` releases all entries and the array itself.

`spdk_strcpy_replace()` copies `src` to `dst` while replacing all occurrences of `search` with `replace`, after precomputing required output size. It returns `-EINVAL` for null arguments or insufficient destination space.

Important caveats are destructive parsing in `spdk_parse_ip_addr()` and `spdk_strsepq()`, unsigned-only numeric wrappers, and caller ownership of allocated format/string-array results.
