# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/net80211_crypto.h

802.11 crypto constants, key structures, and cipher plugin interface.

Key responsibilities:
- Defines WPA/optional IE size limits and MLME operation constants.
- Defines cipher IDs for WEP, TKIP, AES-OCB, AES-CCM, CKIP, and none.
- Defines key buffer/MIC sizes, key flags, default key flag, WEP IV/key-id/CRC constants, extended-IV constants, and maximum key count.
- Defines hardware key index type and no-key sentinel.
- Under `_KERNEL`, defines cipher operation table for attach/detach, key validation, encap/decap, MIC add/check.
- Defines `ieee80211_key` with key material, flags, hardware indexes, rx/tx sequence counters, cipher pointer, and private cipher state.
- Defines per-interface crypto state with network keys, default transmit key, hardware key capacity, and hardware key allocation/delete/set/update callbacks.
- Provides macros for key update, device key operations, cipher attach/detach, and MIC helpers.
- Declares crypto attach/detach, cipher register/unregister, and key reset functions.

Dependencies:
- Includes `sys/net80211_proto.h`; kernel builds also use STREAMS message blocks and MAC headers.

Notable risks:
- Cipher numeric ordering is documented as significant and must not be reordered.
- Key sequence counters and software/hardware crypto flags are security-sensitive.
- Hardware key callback failure handling must avoid installing partially configured keys.
