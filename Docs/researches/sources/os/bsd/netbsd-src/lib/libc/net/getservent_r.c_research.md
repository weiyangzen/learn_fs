# File Research: sources/os/bsd/netbsd-src/lib/libc/net/getservent_r.c

Core reentrant implementation for the services database. `_servent_open()` prefers `_PATH_SERVICES_CDB` via `cdbr_open()` and falls back to `_PATH_SERVICES` opened as a close-on-exec plain file; it also resets cached line, alias, and CDB buffer storage when opening fresh.

Plain-file parsing uses `fparseln()` and splits service lines into name, port/protocol, and aliases, growing the alias vector as needed. CDB iteration uses `cdbr_get()` and `_servent_parsedb()`, which decodes binary records into `struct servent`, copies data into `sd->cdb_buf` when not staying open, and grows alias storage with `reallocarr()`.

`setservent_r()` opens and marks stay-open state, `endservent_r()` closes and frees all dynamic buffers, and `getservent_r()` selects either CDB iteration or plain-file parsing.
