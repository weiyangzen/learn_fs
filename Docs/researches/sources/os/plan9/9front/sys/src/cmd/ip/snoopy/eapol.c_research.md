# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/eapol.c

This module decodes EAP over LAN headers. The header contains version, type, and data length.

The mux table maps EAPOL packet types to `eap`, start, logoff, key, and ASF alert. `p_compile` supports selecting these sub-protocols. `p_filter` matches type after consuming the EAPOL header.

`p_seprint` validates the header, truncates the message to the EAPOL payload length, demuxes based on type, and prints type name, version, and data length.
