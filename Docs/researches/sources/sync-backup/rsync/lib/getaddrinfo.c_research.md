# sources/sync-backup/rsync/lib/getaddrinfo.c

Purpose: provides IPv4-only fallback implementations of `getaddrinfo`, `freeaddrinfo`, `gai_strerror`, and `getnameinfo` for platforms missing them.

Important APIs/types/functions: public `getaddrinfo`, `freeaddrinfo`, `gai_strerror`, and `getnameinfo`; helpers `check_hostent_err`, `canon_name_from_hostent`, `get_my_canon_name`, `get_canon_name_from_addr`, `alloc_entry`, `getaddr_info_single_addr`, `getaddr_info_name`, `gethostnameinfo`, and `getservicenameinfo`. Allocation hooks are `SMB_MALLOC` and `SMB_STRDUP`.

Control flow: `getaddrinfo` normalizes null hints, rejects unsupported families, defaults socket type to `SOCK_STREAM`, and routes to single-address handling for null/empty/numeric/passive nodes or to `gethostbyname` for hostnames. Single-address handling creates one `addrinfo` with `sockaddr_in` and may resolve a canonical name. Hostname handling creates one linked `addrinfo` per IPv4 address returned by `h_addr_list`. `getnameinfo` validates arguments and `AF_INET`, then formats hostname and/or service by reverse lookup unless numeric flags require direct numeric output.

State and persistence behavior: no global state. Each result list owns heap-allocated `addrinfo`, `sockaddr_in`, and optional canonical-name strings, released by `freeaddrinfo`.

Dependencies/integration: includes `rsync.h`, which pulls in `addrinfo.h` macro renames when needed. It uses legacy resolver APIs (`gethostbyname`, `gethostbyaddr`, `getservbyport`, `inet_pton`, `inet_ntoa`) and maps their errors to `EAI_*`.

Risks/test signals: fallback is IPv4-only, service parsing accepts only numeric strings via `atoi`, and `AI_NUMERICSERV` is incorrectly involved in canonical-name gating rather than service lookup. Resolver APIs used here are not thread-safe. Tests should cover passive null host, loopback fallback, numeric host rejection, multiple A records, canonical-name allocation failure paths, service buffer truncation, `NI_NAMEREQD`, and unsupported families.
