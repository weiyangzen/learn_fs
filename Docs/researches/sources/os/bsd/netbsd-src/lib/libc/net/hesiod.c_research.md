# File Research: sources/os/bsd/netbsd-src/lib/libc/net/hesiod.c

Thread-safe Hesiod resolver implementation built around resolver-state APIs such as `res_nmkquery()` and `res_nsend()`. `hesiod_init()` allocates a context, reads `/etc/hesiod.conf` or compiled defaults, and honors `HESIOD_CONFIG` / `HES_DOMAIN` only when not running set-id.

`hesiod_to_bind()` converts a Hesiod name/type pair into a DNS name, handling `name@rhs` forms and `rhs-extension` lookups. `hesiod_resolve()` performs TXT lookups against the configured class order, while `get_txt_records()` constructs DNS queries, validates answer boundaries, filters TXT answers by class/type, and returns a NULL-terminated string vector.

The bottom of the file implements the older `hes_*` compatibility interface using one static context and translated Hesiod error codes.
