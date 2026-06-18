## sources/security-integrity/attr/libmisc/quote.c

Purpose: quote selected characters and backslashes using octal escapes.

`quote` scans for backslash or caller-specified quote characters, returns the original string if no quoting is needed, or a static grown buffer containing escaped text. State is static and reused. Dependencies are `high_water_alloc` and C string functions. Risks are non-thread-safe return storage, caller must handle `NULL` on allocation failure, and only selected characters are escaped, not all non-printables. Tests are output path/name quoting in `getfattr` and `setfattr` restore files.
