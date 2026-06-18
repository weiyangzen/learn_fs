# sources/sync-backup/rsync/lib/inet_pton.c

Purpose: fallback `inet_pton` implementation for parsing IPv4 and optionally IPv6 presentation addresses into network-order binary form.

Important APIs/types/functions: public `inet_pton`, static `inet_pton4`, optional static `inet_pton6`, and constants `NS_INT16SZ`, `NS_INADDRSZ`, and `NS_IN6ADDRSZ`.

Control flow: `inet_pton` switches on address family, returning 1 for valid parse, 0 for invalid text, or -1 with `EAFNOSUPPORT`. IPv4 strictly accepts dotted decimal quads: four octets, no shorthand or hex, each <= 255, and destination untouched on failure. IPv6 parses hex groups, a single `::`, and embedded IPv4 tails, then expands the compressed zero run by shifting bytes manually before copying to destination.

State and persistence behavior: no state. Temporary parse buffers are stack-local and destination is only written after a complete valid parse.

Dependencies/integration: includes `rsync.h`; used by fallback address resolution and socket parsing on systems lacking libc support.

Risks/test signals: IPv4 parser allows leading zeros as decimal, not octal, which is intentional but may differ from `inet_aton`. IPv6 support is gated by `INET6`, not `AF_INET6`. Tests should cover invalid partial writes, multiple `::`, embedded IPv4, overflow groups, too few/many octets, unsupported families, and exact binary output.
