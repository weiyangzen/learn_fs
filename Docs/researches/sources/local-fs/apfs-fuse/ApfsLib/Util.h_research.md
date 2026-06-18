# File Research: sources/local-fs/apfs-fuse/ApfsLib/Util.h

This header declares the utility surface implemented in `Util.cpp`. It includes APFS UUID types and standard C++ string/vector/ostream support.

The API covers Fletcher64 checksum calculation, APFS block verification, zero checks, hex dumping, UUID and byte-string formatting, UTF-8/UTF-32 dump helpers, APFS filename hashing, APFS byte-string comparison, normalized/folded UTF-8 comparison, UTF-8 to UTF-32 conversion, six decompression helpers, password input, integer log2, and printf-style logging helpers.

The logging declarations use GCC-style `format(printf)` attributes, which helps catch mismatched format strings on compatible compilers. MSVC compatibility depends on `Endian.h`’s handling of `__attribute__` in translation units where this header is included indirectly.
