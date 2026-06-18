# File Research: sources/teaching/os161/kern/include/kern/secure.h

Declares HMAC helper functions.

APIs:
- `hmac` computes SHA-256 HMAC and returns a hex-readable hash string.
- `hmac_salted` computes salted HMAC and returns hash and salt strings.
- Callers must free returned strings.

Notable issue:
- Comment says “complient” and describes `hmac_with_salt`, but declared function is `hmac_salted`; documentation and API naming are slightly inconsistent.
