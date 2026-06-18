# File Research: sources/os/bsd/freebsd-src/sbin/dumpon/dumpon.c

Implements `dumpon`, configuring kernel crash dump targets, optional dump compression/encryption, priority insertion/removal, listing, and netdump.

Key responsibilities:
- Parses block-device dump targets, `off`, list mode, netdump parameters, compression flags, encryption key options, priority index, and remove mode.
- Opens dump devices under `/dev` if a bare name is supplied.
- Checks that local dump device size can hold physical memory unless minidumps are enabled or compression/removal applies.
- Configures kernel dump state through `DIOCSKERNELDUMP`.
- Lists current dump devices through `kern.shutdown.dumpdevname`.
- Lists verbose netdump configuration from `_PATH_NETDUMP` via `DIOCGKERNELDUMP`.

Netdump behavior:
- Requires server and client IPv4 addresses; gateway is optional.
- Resolves server names with `getaddrinfo()`.
- Finds default gateway on an interface using `getifaddrs()` plus routing-table `sysctl(NET_RT_DUMP)`.
- Warns if the configured interface is down.

Crypto behavior when built with OpenSSL:
- Supports `-k <pubkey>` and optional `-C chacha|aes-cbc`.
- Generates a random one-time kernel dump key.
- Encrypts it with RSA OAEP using the supplied public key.
- Rejects RSA keys below approximately 112 symmetric security bits.
- Rejects AES-CBC with compression.
- Runs key generation in a child that enters Capsicum capability mode, returning the configured structure and encrypted key via pipe.
- Explicitly zeroes key material before freeing.

Compression behavior:
- `-z` selects gzip; `-Z` selects zstd.
- Mutually exclusive.
- If kernel rejects compression with `EINVAL`, retries without compression and warns.

Risks and constraints:
- IPv4-only netdump configuration in this implementation.
- Encryption support depends on OpenSSL build option.
- Uses legacy OpenSSL RSA APIs guarded by compatibility defines.
- `find_gateway()` assumes route messages contain expected destination, mask, and gateway sockaddr fields.
