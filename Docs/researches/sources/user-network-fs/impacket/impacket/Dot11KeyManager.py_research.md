# sources/user-network-fs/impacket/impacket/Dot11KeyManager.py

Purpose: `Dot11KeyManager.py` is a small BSSID-to-key registry for 802.11 decoders, allowing protected wireless frames to find the key associated with an access point address.

Important APIs, types, and functions: `KeyManager` exposes `add_key(bssid, key)`, `replace_key(bssid, key)`, `get_key(bssid)`, and `delete_key(bssid)`. The private `__get_bssid_hasheable_type()` validates that BSSID input is a list, tuple, or `array.array` and converts it to a tuple for dictionary use.

Control flow: Add, replace, and get normalize the BSSID to a tuple and operate on `self.keys`. `add_key()` refuses to overwrite an existing entry and returns a boolean. `replace_key()` always stores the key and returns true. `get_key()` returns the key or `False` if absent.

State and persistence behavior: State is the in-memory `self.keys` dictionary. There is no file or network persistence. Keys remain until deleted or the manager object is discarded.

Dependencies and integration points: The only dependency is `array.array` for accepted BSSID input. `ImpactDecoder.BaseDot11Decoder.find_key()` calls `key_manager.get_key()` and WEP decoding uses that key to decrypt frames by BSSID.

Risks: `delete_key()` appears broken: it normalizes the BSSID to a tuple, then checks `if not isinstance(bssid, list)` and raises, so normal valid inputs cannot pass deletion. Returning `False` for absent keys can collide with a legitimate falsey key value. The class performs no key length or type validation and is not thread-safe.

Test signals: Tests should cover tuple/list/array BSSID normalization, add duplicate behavior, replacement, lookup miss behavior, and the `delete_key()` bug. Decoder integration tests should verify that WEP frames find the correct BSSID-derived key.
