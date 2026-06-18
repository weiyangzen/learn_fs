# sources/user-network-fs/samba/source3/lib/gencache.h

Purpose: declares the generic cache API for timeout-bound string and blob values.

Important APIs/types/functions: `gencache_set()`, `gencache_get()`, `gencache_del()`, `gencache_parse()`, blob get/set, iterators, `struct gencache_timeout`, and `gencache_timeout_expired()`.

Control flow: callers set absolute-timeout entries, fetch or parse them, and iterate pattern-matching keys.

State/persistence behavior: the API exposes talloc-owned outputs and an opaque timeout object; persistence is handled by `gencache.c`.

Dependencies/integration: included by idmap/name-map/WINS utilities and tests.

Risks/test signals: callback ownership and expiration semantics must be respected. Compile and local cache torture tests validate the contract.
