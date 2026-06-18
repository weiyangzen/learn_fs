# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/util.c

`util.c` provides shared low-level helpers for `isakmpd`: big-endian integer encode/decode, zero-buffer tests, hex/raw conversion, service-name-to-port parsing, sockaddr parsing/formatting, sockaddr address/port accessors, network-address formatting, secret-file permission checks, monotonic timeout calculation, and bounded substring expansion.

`text2sockaddr()` is the most involved helper. It uses numeric `getaddrinfo()` unless name lookups are enabled, supports the special `default` keyword by querying the route socket, and can resolve interface names to IPv4/IPv6 addresses or netmasks with link-local IPv6 preference handling.

Security-relevant details: `check_file_secrecy_fd()` rejects secret files owned by neither root nor the process user and files accessible by group/other. Address parsing defaults to numeric-only to avoid daemon stalls from DNS unless `allow_name_lookups` is set.

The file is common infrastructure for transport binding, config parsing, certificate printable conversion, UI hex decoding, and logging/reporting.
