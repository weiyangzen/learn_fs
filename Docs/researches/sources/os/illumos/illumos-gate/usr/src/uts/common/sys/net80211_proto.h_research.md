# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/net80211_proto.h

802.11 wire protocol definitions for net80211.

Key responsibilities:
- Defines address helpers, ACK size, physical modes, PHY types, operating modes, and protection modes.
- Defines packed frame structures for data, QoS data, 4-address frames, LLC/SNAP, management notification, RTS/CTS/ACK/PS-Poll/CF-End/BAR control frames, TIM IE, WPA IE, WME parameter/info/TSPEC elements, 802.11n action frames, HT capability IE, and HT information IE.
- Defines frame-control type/subtype/direction bits, sequence/fragment masks, sequence arithmetic macros, QoS masks, WME AC/TID mapping, management action constants, block-ack masks, and HT capability/parameter/info masks.
- Defines management information element lengths, capability flags, element IDs, OUIs, authentication algorithms/sequences, reason codes, status codes, WEP constants, MTU/min/max frame lengths, association ID limits, RTS/fragment thresholds, rate-fix flags, and beacon offset bookkeeping.
- Uses packed layout around all wire structures.

Dependencies:
- Consumed by `net80211.h`, `net80211_crypto.h`, and 802.11 frame parsing/building code.

Notable risks:
- Packed wire structures and bit masks must match IEEE 802.11 frame layout exactly.
- Some constants are duplicated with crypto headers; changes must stay synchronized.
- Variable-length IE structures require careful length validation before access.
