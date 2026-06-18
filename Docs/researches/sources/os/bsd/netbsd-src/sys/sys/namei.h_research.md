# File Research: sources/os/bsd/netbsd-src/sys/sys/namei.h

## Purpose
Generated pathname lookup and name cache header. It defines `pathbuf`, `nameidata`, component lookup flags, name cache internals, lookup/cache APIs, and namei cache statistics.

## Main API
- Path buffer routines: `pathbuf_create`, `pathbuf_assimilate`, `pathbuf_copyin`, `pathbuf_destroy`, `pathbuf_copystring`, `pathbuf_stringcopy_get`, `pathbuf_stringcopy_put`.
- Lookup structures: `struct componentname`, `struct nameidata`.
- Operation constants: `LOOKUP`, `CREATE`, `DELETE`, `RENAME`.
- Lookup flags: `LOCKLEAF`, `LOCKPARENT`, `FOLLOW`, `TRYEMULROOT`, `NOCACHE`, `NOCROSSMOUNT`, `RDONLY`, `ISDOTDOT`, `MAKEENTRY`, `ISLASTCN`, `REQUIREDIR`, `CREATEDIR`, and masks.
- Initialization macros: `NDINIT`, `NDAT`.
- Kernel simple lookup APIs: `namei_simple_kernel`, `namei_simple_user`, `nameiat_simple*`.
- Name cache APIs: `cache_lookup`, `cache_enter`, `cache_purge`, `cache_revlookup`, `cache_cross_mount`, `cache_lookup_mount`, vnode/cache init/fini routines.
- Statistics: `struct nchstats`.

## Dependencies
Kernel/module sections require vnode-related types, credentials, locks, queues, mutexes, and memory allocation. Private namecache sections use red-black trees.

## Risks and Notes
The file is generated from `namei.src`; edits must be made to the source generator input. `pathbuf` lifetime rules are explicit: callers must keep the path buffer alive until `nameidata` use is finished. Name cache internals have carefully documented lock ownership fields.
