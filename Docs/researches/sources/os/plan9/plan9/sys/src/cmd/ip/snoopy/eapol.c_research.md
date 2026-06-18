# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/eapol.c

`snoopy` EAP over LAN decoder.

Key behavior:
- Parses EAPOL version, type, and payload length.
- Filters/demuxes EAPOL packet type: EAP, start, logoff, key, ASF alert.
- Truncates message to EAPOL payload length and formats type/version/data length.

Integration:
- Reached from Ethernet EtherType `0x888e`.
- Demuxes key packets to `eapol_key`.

Risks and notes:
- Start/logoff/asf alert fall back to dump unless corresponding protocol exists.
