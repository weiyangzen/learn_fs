# sources/user-network-fs/impacket/tests/dot11/test_RadioTapDecoder.py

Purpose: Verifies end-to-end decoder chaining from RadioTap through Dot11 data, LLC, and SNAP layers.

Important APIs, types, and functions: Uses `RadioTapDecoder.decode`, `get_protocol`, and protocol classes `RadioTap`, `Dot11`, `Dot11DataFrame`, `LLC`, `SNAP`, and `Dot11WPA`.

Control flow: `setUp` decodes a raw RadioTap ARP packet and stores consecutive `child()` nodes. Tests assert class types at each decoded layer and verify protocol lookup returns instances already present in the decoded stack, while absent protocols return `None`.

State and persistence behavior: Decoder state is in-memory protocol-chain state; no persistent storage.

Dependencies and integration points: Integrates `ImpactDecoder` with `impacket.dot11` and `ImpactPacket` payload discovery. ARP/Data assertions are commented out, so coverage stops at SNAP for protocol types.

Risks: Reliance on stringified class names for Python 2 compatibility is brittle but intentional. `get_protocol` correctness depends on child-chain traversal order.

Test signals: Good signal for decoder dispatch, protocol stack linking, and protocol lookup failure behavior.
