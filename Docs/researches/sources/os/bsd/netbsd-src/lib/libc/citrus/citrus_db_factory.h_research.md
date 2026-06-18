# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_db_factory.h

Interface for constructing serialized Citrus DB regions.

Key behavior:
- Declares opaque `_citrus_db_factory`.
- Defines `_citrus_db_hash_func_t`.
- Declares create/free, add raw/string/typed entries, size calculation, and serialization.

This is used by tools that compile text lookup data into DB form.
