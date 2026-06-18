# File Research: sources/virtualization/nbd/cliserv.h

Shared protocol and helper declarations for NBD client/server code.

It includes network headers, `nbd.h`, large-file fallback definitions, GCC noreturn/unused compatibility macros, extern protocol magic constants, `INIT_PASSWD`, helper prototypes, network-byte-order helpers, full read/write helper prototypes, and the default NBD port `10809`.

It also defines key NBD option negotiation constants: export selection, abort, list, STARTTLS, INFO, GO, structured replies, reply types/errors, global flags, client flags, and info type identifiers.

This header is central glue between `nbd-client.c`, server code, transaction tools, and shared protocol handling.
