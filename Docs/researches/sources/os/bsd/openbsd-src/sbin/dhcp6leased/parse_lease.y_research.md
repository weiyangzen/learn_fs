# File Research: sources/os/bsd/openbsd-src/sbin/dhcp6leased/parse_lease.y

Yacc grammar and lexer for persisted `dhcp6leased` lease files.

It parses lease lines of the form `ia_pd <IAID> <IPv6 prefix> <prefix length>` into an `imsg_ifinfo` prefix array. Prefix lengths must be 1 through 128, prefixes must parse with `inet_pton(AF_INET6, ...)`, and invalid entries clear the affected prefix length.

The lexer mirrors the main parser’s quoted string, comment, number, keyword, and string handling while reusing shared file stack helpers from `parse.y`. Notable boundary detail: it rejects IA IDs greater than `MAX_IA`, but the destination array is sized `MAX_IA`, so an IA ID exactly equal to `MAX_IA` would address one past the valid index.
