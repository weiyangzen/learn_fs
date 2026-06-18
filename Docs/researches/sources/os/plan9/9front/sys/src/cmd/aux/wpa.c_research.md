# File Research: sources/os/plan9/9front/sys/src/cmd/aux/wpa.c

Implements WPA/WPA2 supplicant behavior for Plan 9 wireless devices.

Key responsibilities:
- Builds WPA/RSN information elements from kernel-reported BSS RSNE data.
- Chooses pairwise/group cipher support between TKIP and CCMP.
- Integrates with factotum for PSK, MSCHAPv2, identity lookup, PMK storage, and PTK derivation.
- Processes EAPOL Ethernet frames and implements WPA key handshake logic.
- Calculates and verifies EAPOL MICs using HMAC-MD5 or HMAC-SHA1 depending on key descriptor version.
- Unwraps encrypted key data using RC4 or AES key unwrap.
- Implements EAP Identity, MSCHAPv2, EAP-TTLS, and PEAP client paths.
- Tunnels TLS records through EAP fragmentation and derives PMK from TLS keying material.
- Installs pairwise and group keys by writing `rxkey`, `txkey`, and `rxkeyN` commands to the device control file.
- Reconnects after deassociation and can background itself.

Important interfaces:
- Talks to the network device through `dial(dev!0x888e, ..., devdir, &cfd)` and `ifstats`.
- Uses `/mnt/factotum/rpc` and `/mnt/factotum/ctl`.
- Uses libsec/libauth primitives: TLS, HMAC, AES, RC4, `auth_rpc`, `auth_respond`, `auth_getuserpasswd`.

Notes:
- `newptk` gates pairwise key installation to avoid reinstalling PTK on replayed retransmits.
- `lastrepc` rejects replay counters that do not strictly increase.
- `-1` forces WPA1/TKIP defaults, `-2` forces RSN/CCMP defaults, `-p` prompts/warms credentials, and `-s` sets ESSID.
