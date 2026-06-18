# File Research: sources/os/plan9/plan9/sys/src/9/ip/esp.c

Implements IPsec Encapsulating Security Payload for IPv4 and IPv6, focused on tunnel mode.

Key responsibilities:
- Registers protocol `esp` for IP protocol number 50.
- `espconnect` binds a remote address and SPI, or allocates a random inbound SPI when `*` is supplied.
- Maintains per-conversation `Espcb` state: direction, optional user header mode, SPI, sequence, cipher algorithm/state, auth algorithm/state, IV/block/auth lengths, and function pointers.
- `espkick` encapsulates outgoing packets: optional user header parsing, ESP padding/trailer, encryption, ESP header construction, authentication, and dispatch through `ipoput4` or `ipoput6`.
- `espiput` receives ESP packets: determines IP version, extracts SPI/address tuple, finds inbound conversation, authenticates, decrypts, strips ESP/IP headers and trailer, optionally prepends user header, and queues plaintext.
- `espctl` supports `esp <alg> <key>`, `ah <alg> <key>`, `header`, and `noheader`.
- `espadvise` maps ICMP/ICMPv6 errors to matching ESP conversations.
- `espstats`, `esplocal`, and `espremote` expose status.

Algorithms:
- Encryption: `null`, `des_56_cbc`, `des3_cbc`, `aes_128_cbc`, `aes_ctr`.
- Authentication: `null`, `hmac_sha1_96`, `aes_xcbc_mac_96`, `hmac_md5_96`.
- Includes local HMAC-MD5/SHA1 helpers and Plan 9 libsec AES/DES setup.

Notable constraints:
- Comments state tunnel mode only; transport mode is TODO.
- Block lists are concatenated before cryptographic processing where needed.
