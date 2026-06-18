# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lookup_factory.c

Converter from plain lookup text to compiled Citrus lookup DB.

Key behavior:
- Reads input lines with `fgetln`.
- Strips comments and whitespace.
- Extracts the first token as key, lowercases it, and stores the rest of the line as data.
- Uses `_citrus_db_factory` with `_db_hash_std`.
- Serializes with lookup magic `LOOKUP\0\0` and writes the region to output.

Purpose:
- Build-time support for faster runtime lookup files.
