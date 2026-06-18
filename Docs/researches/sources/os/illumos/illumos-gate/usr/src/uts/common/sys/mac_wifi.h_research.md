# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_wifi.h

Purpose: Defines the WiFi MAC-type plugin contract for GLDv3 wireless drivers.

Key definitions:
- Plugin identifier: `MAC_PLUGIN_IDENT_WIFI`.
- Maximum WiFi header size: `WIFI_HDRSIZE`.
- WiFi statistics enum beginning at `MACTYPE_STAT_MIN`.
- Security modes: `WIFI_SEC_NONE`, `WIFI_SEC_WEP`, `WIFI_SEC_WPA`.
- `wifi_data_t`: option flags, BSSID, operation mode, security header allocation policy, and QoS padding.

Important details:
- `wd_opts` is reserved as an extensibility bitmap so drivers and plugin can evolve independently.
- `wd_qospad` handles hardware needing 802.11 QoS/4-address header padding.

Relevance to subset A: Network plugin ABI, outside filesystem focus.
