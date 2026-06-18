# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/eapol_key.c

`snoopy` EAPOL-Key decoder and RC4 key descriptor formatter.

Key behavior:
- Parses key descriptor type and demuxes descriptor type `1` to `rc4keydesc`.
- `rc4keydesc` formatter parses key length, replay counter, IV, index, digest, and trailing data length.

Integration:
- Reached from `eapol.c` type `Key`.
- `rc4keydesc.c` is a placeholder; real `Proto rc4keydesc` is here.

Risks and notes:
- Several multi-byte RC4 descriptor fields are wider than `NetS()` output shown by formatter, so printed replay/IV/MD values are abbreviated.
