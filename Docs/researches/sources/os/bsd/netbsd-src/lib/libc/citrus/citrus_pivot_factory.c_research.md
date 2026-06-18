# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_pivot_factory.c

Read completely: 231 lines.

This file compiles text pivot mapping data into the Citrus pivot DB format. It parses input lines of the form `source target value`, strips comments beginning with `#`, groups rows by source encoding name, stores target/value mappings in per-source database factories, then serializes a top-level `_CITRUS_PIVOT_MAGIC` DB containing per-source `_CITRUS_PIVOT_SUB_MAGIC` sub-DBs.

Key functions: `find_src` creates or finds a source entry and DB factory; `convert_line` tokenizes and validates one line; `dump_db` serializes nested DB regions; `_citrus_pivot_factory_convert` streams all input lines, builds the DB, and writes the serialized region.

Important interactions: uses `_citrus_db_factory`, `_citrus_region`, BCS token helpers, and magic strings from `citrus_pivot_file.h`. This is a build/tooling-side converter rather than an iconv runtime mapper.

Security/reliability notes: parsing is bounded by `LINE_MAX` stack buffers and `snprintf`. Numeric parsing rejects trailing nonnumeric data. `dump_db` allocates serialized subregions and transfers ownership into the DB factory; it frees only the most recent temporary pointer on failure, so review of `_db_factory_add_by_s` ownership semantics is important when changing this path.
