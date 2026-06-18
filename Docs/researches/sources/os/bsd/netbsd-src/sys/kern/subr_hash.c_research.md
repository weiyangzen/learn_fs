# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_hash.c

Read completely: 268 lines.

Provides generic kernel hash-table allocation and hash-statistics registration. `hashinit()` rounds the requested element count up to a power of two, allocates an array of list heads for `HASH_LIST`, `HASH_PSLIST`, `HASH_SLIST`, or `HASH_TAILQ`, initializes each bucket, and returns a mask. `hashdone()` frees the table using the mask and bucket-head size.

The second half implements `hashstat_register()` and the `kern.hashstat` sysctl. Registered providers supply `hashstat_sysctl` records; the sysctl supports list/describe behavior and query-by-name through `CTL_QUERY`, dropping the sysctl lock while traversing providers under `hashstat_lock`.

Risks and notes:
- `elements` must be nonzero; oversized requests are capped before rounding.
- Query names are copied in from userland and unmatched queries return `ENOENT`.
- Provider callbacks run under the hashstat reader lock, so callback locking behavior matters.
