# File Research: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp.h

Public Service Discovery Protocol header.

Key behavior:
- Defines SDP data element type/size encodings and concrete element tags for integers, UUIDs, strings, sequences, alternatives, booleans, URLs, and nil.
- Defines Bluetooth protocol UUIDs, service class IDs, universal attributes, language-base offsets, profile attributes, PDU headers, PDU IDs, and SDP error codes.
- Defines local sdpd control path `/var/run/sdp`, local MTU, and NetBSD-private record insert/update/remove PDUs.
- Defines `sdp_data_t` cursor slices and opaque `sdp_session_t`.
- Declares modern SDP APIs for sessions, record insert/update/remove, service search/attribute/search-attribute, data match/get/put/set, validation, sizing, and printing.
- Uses `__RENAME` to expose modern APIs under internal `_sdp_*` names when not building `SDP_COMPAT`.
- Under `SDP_COMPAT`, defines old API types, byte-order macros, int128 structs, attribute structs, profile structs, compatibility functions, and old byte-stream get/put macros.

Dependencies:
- `<uuid.h>`, public `bluetooth.h`, and endian macros.

Notes:
- This header carries both modern and legacy source-compatibility APIs; build flags determine which naming surface is visible.
