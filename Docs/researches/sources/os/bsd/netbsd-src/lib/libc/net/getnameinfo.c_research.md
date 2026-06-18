# File Research: sources/os/bsd/netbsd-src/lib/libc/net/getnameinfo.c

Read completely: 639 lines.

This file implements `getnameinfo`, dispatching by sockaddr family to IPv4/IPv6, AppleTalk, link-layer, and local-domain formatters. It supports numeric and reverse-name host output, service-name lookup, `NI_NUMERICHOST`, `NI_NAMEREQD`, `NI_NUMERICSERV`, `NI_DGRAM`, IPv6 textual scope IDs, and link-layer formatting by interface type.

`getnameinfo_inet` validates sockaddr length, resolves services via `getservbyport_r` unless numeric service is requested, suppresses reverse DNS for multicast/experimental/unspecified/link-local cases, performs `gethostbyaddr_r` for names, and falls back to numeric text when allowed. IPv6 helpers append `%scope` using interface names for link-local scopes where possible. Link-layer helpers format `sockaddr_dl` as `link#N`, Econet-style addresses, IEEE1394 UID hex, or colon-separated hex bytes.

Security/reliability notes: short output buffers return `EAI_MEMORY` or `EAI_OVERFLOW` depending on path. Some non-INET family helpers assume non-null host buffers when formatting; typical callers pass host storage when requesting those families.
