# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/mppc.c

Implements Microsoft Point-to-Point Compression (MPPC) and optional RC4-based encryption support for PPP CCP.

Key behavior:
- Compression state `Cstate` keeps 8 KiB history arenas, hash table, packet count, reset/front flags, bit output register, and optional RC4 key state.
- `compinit` initializes history/hash state and encryption key material from `PPP.key` when `sendencrypted` is set.
- `comp` prepends protocol, compresses with `comp2`, chooses compressed vs expanded/plain output, sets MPPC count/flags, and encrypts payload if negotiated.
- `comp2` performs LZ-style hash matching against current/old history, emits literals through `complit` and copies through `compcopy`.
- `compfront` and `compreset` manage history window rollover and reset flags.
- `uncomp` strips MPPC header, calls `uncomp2`, returns CCP reset requests on failure, and extracts the original protocol.
- `uncomp2` validates packet counts, handles reset/front/encryption flags, decodes literal/copy bitstream into history, and returns reconstructed payload.
- `setkey` derives RC4 keys using SHA-1 padding sequence.
- Tail functions `ipcheck` and `hischeck` are debug validators for reconstructed IP/TCP/UDP checksums.

Integration points:
- Exposes `cmppc` and `uncmppc` virtual tables consumed by `ppp.c` CCP negotiation.
- Uses PPP `Block`, LCP reset request allocation, RC4/SHA from `libsec`, and checksum helpers from `ipaux.c`.

Risks and notes:
- Packet count continuity is strict; missing packets trigger reset request.
- Several debug logs are unconditional in decompression paths.
- `comp` requires two bytes of headroom and calls `sysfatal` if absent.
