# File Research: sources/os/plan9/9front/sys/src/9/ip/esp.c

Implements IPsec ESP protocol handling for IPv4 and IPv6, primarily tunnel mode. It supports null encryption/authentication, DES/3DES CBC, AES CBC, AES CTR-named mode, HMAC-SHA1-96, and HMAC-MD5-96.

Key responsibilities:
- Registers protocol `esp` for IP protocol number 50.
- Connects ESP conversations to remote address/SPI pairs in `espconnect()`.
- Encapsulates outbound packets in `espkick()`.
- Decapsulates inbound ESP packets in `espiput()`.
- Handles algorithm control commands through `espctl()`: `esp`, `ah`, `header`, `noheader`.
- Handles ICMP advice in `espadvise()` and exposes stats/local/remote formatting.

Important implementation details:
- `Espcb` stores SPI, sequence, selected ESP/AH algorithm state, IV length, block length, auth length, and callback pointers.
- Incoming conversations match by SPI only through `convlookup()`.
- Outbound packets are padded to satisfy ESP cipher/auth alignment, encrypted, then authenticated.
- Inbound packets authenticate before decryption, validate payload sizing, strip ESP/IP headers, and optionally prepend a small user header.
- Algorithm keys are accepted as hex strings and zeroed after conversion.
- IVs are generated with `prng()` during algorithm initialization and embedded at the start of encrypted payload.

Dependencies and integration:
- Uses `libsec` DES, AES, MD5, SHA1, and secure allocation helpers.
- Sends packets through `ipoput4()` or `ipoput6()`.
- Receives ICMP advice through protocol `advise`.

Research notes:
- Header comments explicitly say transport mode is TODO and tunnel mode is the current implementation.
- Replay protection state (`window`) exists in `Espcb` but is not actively enforced in the read path shown.
- The AES CTR function is structurally identical to CBC-style state updates here, so algorithm naming should be treated cautiously.
