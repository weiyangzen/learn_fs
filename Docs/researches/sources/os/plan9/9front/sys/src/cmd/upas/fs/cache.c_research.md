# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/cache.c

This file manages message caching for `upas/fs`, including header/body fetching, LRU eviction, digesting, and index readiness.

Key behavior:
- Tracks cached byte counts per message and mailbox and maintains an LRU list of top-level messages.
- `cachefree` releases message body/header buffers, MIME metadata, references, and mailbox-specific decache hooks.
- `fetch` grows message buffers, calls mailbox backend `fetch`, squeezes embedded NUL and CR bytes, and handles Gmail size shifts.
- `cacheheaders` fetches enough data to parse headers, using partial fetch for large messages.
- `cachebody` fetches complete message content, adjusts size for stripped bad chars, computes SHA1 digest, counts lines, and parses MIME/body structure.
- `ensurecache` forces indexed cache state and digest/npart availability for serving and indexing.

Integration and risks:
- Central to all backends with `Mailbox.fetch`, especially IMAP and mdir.
- Uses `Maxmsg`, `cachetarg`, `Cidx/Cheader/Cbody` state flags from `dat.h`.
- Several paths assume pointer arithmetic is valid and assert heavily; malformed backend size data can trip fatal assertions.
