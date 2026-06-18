# File Research: sources/os/bsd/netbsd-src/lib/libresolv/hmac_link.c

Read completely: 472 lines.

Implements the DST algorithm binding for HMAC-MD5. It stores precomputed 64-byte inner and outer pads in an `HMAC_Key`, supports incremental signing and verification over MD5 contexts, converts raw/shared-secret bytes into pad form, and registers these operations in `dst_t_func[KEY_HMAC_MD5]`.

Keys longer than the HMAC block length are first MD5-hashed. File-format conversion emits and parses a `Key: <base64>` line under the generic DST private-key header, while DNS-key conversion extracts the original shared secret from the XORed pad.

Verification requires a 16-byte signature and compares with `memcmp()`. Contexts are heap-allocated for incremental use and freed on finalization; some error paths can leave caller-owned context handling ambiguous, matching the legacy API style.
