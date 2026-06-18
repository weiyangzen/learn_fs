# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_mapper.c

Generic runtime loader/cache for Citrus mapper modules.

Key behavior:
- `_citrus_mapper_create_area` validates a mapper area by checking for `mapper.dir`, stores base directory, and initializes a fixed hash cache.
- `lookup_mapper_entry` maps `mapper.dir`, finds a mapper line, and splits it into module and variable arguments.
- `mapper_open` loads a module, resolves mapper getops, validates required ABI methods, allocates traits, and calls module init.
- `_citrus_mapper_open` caches mappers by map name with reference counts.
- `_citrus_mapper_open_direct` bypasses `mapper.dir`.
- `_citrus_mapper_close` decrements reference counts, removes cached entries at zero, and unloads modules.
- `_citrus_mapper_set_persistent` marks a mapper as never freed.

Concurrency:
- Uses a process-wide rwlock around area creation and cache/refcount mutation.
