# File Research: sources/os/plan9/9front/sys/src/9/port/wifi.c

Shared 802.11 station-management, Ethernet bridging, and WPA/TKIP/CCMP support for Plan 9 Ethernet Wi-Fi drivers.

Key responsibilities:
- Parses 802.11 headers, source/destination address selection, QoS header length, SNAP headers, beacons, probe responses, auth responses, assoc responses, deauth frames, and encrypted frames.
- Converts inbound 802.11 data frames to Ethernet frames and outbound Ethernet frames to 802.11 data frames with SNAP encapsulation.
- Maintains a small table of discovered `Wnode` BSS entries, selects a matching BSS by ESSID/BSSID, sends probes/auth/association requests, and runs scan/association maintenance in kernel processes.
- Tracks node status transitions: connecting, authenticated, need authentication, unauthenticated, associated, unassociated, and blocked.
- Implements simple transmit rate adaptation using successful transmit counts and `wifitxfail()`.
- Provides `wifiattach()`, `wificfg()`, `wifictl()`, and `wifistat()` for driver integration and control/status file plumbing.
- Parses key specifications, stores keys in secure allocations, handles RSN/WPA element control, and clears keys on deauthentication.
- Implements TKIP key mixing, Michael MIC, RC4 encryption/decryption, CCMP AES-CCM encryption/decryption, replay checks through TSC counters, and key masking in status output.

Dependencies:
- Uses Plan 9 Ethernet/netif queues, `libsec` RC4/AES helpers, block buffers, timers/ticks, command parsing, and driver-supplied `transmit(Wifi*, Wnode*, Block*)`.

Notable behavior:
- When a WPA/RSN association is blocked pending keys, only EAPOL (`0x888e`) frames are passed.
- Deauthentication of the active BSS flushes Ethernet output and notifies EAPOL listeners with a zero-length packet.
- `wifiprobe()` with empty ESSID can call the driver transmit hook with a nil block to tune/scan channels.
