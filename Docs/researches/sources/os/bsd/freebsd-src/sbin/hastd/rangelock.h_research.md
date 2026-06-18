# File Research: sources/os/bsd/freebsd-src/sbin/hastd/rangelock.h

`rangelock.h` declares the opaque range-lock API used by HAST code. It forward-declares `struct rangelocks` and exports init/free/add/delete/islocked functions using `off_t` offsets and lengths.

The header deliberately exposes no synchronization primitive or range internals, so callers own concurrency and lifetime discipline around the table.
