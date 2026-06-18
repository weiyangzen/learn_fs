# File Research: sources/os/bsd/netbsd-src/lib/libresolv/res_sendsigned.c

Read completely: 173 lines.

Implements `res_nsendsigned()`, which signs an outbound DNS message with a TSIG key, sends it through a copied resolver state, and verifies the signed reply. It only accepts `NS_TSIG_ALG_HMAC_MD5`, wraps key bytes with `dst_buffer_to_key()`, appends TSIG using `ns_sign()`, and suppresses resolver debug reply printing on the copied state.

The function chooses TCP if the signed message exceeds `PACKETSZ` or `RES_USEVC` is set; otherwise it sets `RES_IGNTC` and retries over TCP if a truncated UDP response arrives and truncation is not ignored by the original state.

On verification failure it prints resolver-debug diagnostics when requested, maps bad input to `EINVAL` and TSIG failure to `ENOTTY`, and frees the copied state, signed message buffer, and DST key.
