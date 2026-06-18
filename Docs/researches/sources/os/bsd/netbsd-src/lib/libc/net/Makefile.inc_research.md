# File Research: sources/os/bsd/netbsd-src/lib/libc/net/Makefile.inc

Read completely: 155 lines.

This make include defines libc networking sources, generated parser/lexer rules, machine-dependent byte-order source inclusion, man pages, and manual-page links for networking APIs.

It adds sources for resolver/base64/ethers/host/network/protocol/service lookups, `getaddrinfo`, `getnameinfo`, interface-name helpers, SCTP calls, and optional Hesiod/IPv6 components. It includes `${ARCHDIR}/net/Makefile.inc` for architecture-specific `htonl`, `htons`, `ntohl`, and `ntohs` implementations.

Security/reliability notes: no runtime behavior, but build composition matters: disabling `USE_INET6` or `MKHESIOD` changes exported libc networking coverage.
