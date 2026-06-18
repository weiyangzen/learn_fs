## sources/user-network-fs/libtirpc/src/des_soft.c

Purpose: Provides `des_setparity`, the DES key utility that forces odd parity in each of the eight key bytes.

Important APIs and control flow: A static `partab[128]` maps the low seven bits of a byte to the corresponding odd-parity byte. `des_setparity(char *p)` loops over eight bytes and replaces each with `partab[*p & 0x7f]`.

State and persistence: The lookup table is process read-only; the caller's key buffer is modified in place.

Dependencies and integration: Used by callers that need DES-compatible key parity before `cbc_crypt`, `ecb_crypt`, or AUTH_DES operations.

Risks and test signals: The function ignores the input high bit by masking with `0x7f`. Tests should verify all output bytes have odd parity, exactly eight bytes are touched, known parity conversions hold, and signed-char inputs behave as intended through the mask.
