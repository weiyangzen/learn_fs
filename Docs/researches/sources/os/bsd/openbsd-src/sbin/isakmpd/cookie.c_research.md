# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/cookie.c

This file generates ISAKMP anti-clogging cookies.

Key responsibilities:
- Computes a cookie using SHA1 over transport endpoint addresses, optional initiator cookie data, and fresh random secret bytes.

Important function:
- `cookie_gen(struct transport *t, struct exchange *exchange, u_int8_t *buf, size_t len)`

Notable behavior:
- Uses destination and source socket addresses from the transport vtable.
- For responder-side exchanges, includes the initiator cookie from the exchange header.
- Mixes in `COOKIE_SECRET_SIZE` bytes from `arc4random_buf`.
- Copies the requested number of digest bytes to the caller buffer.

Dependencies:
- Hash framework via `hash_get(HASH_SHA1)`.
- Transport endpoint accessors.
- Exchange cookie fields.

Research notes:
- The cookie is stateless from the peer perspective but includes endpoint and exchange data to resist request flooding.
