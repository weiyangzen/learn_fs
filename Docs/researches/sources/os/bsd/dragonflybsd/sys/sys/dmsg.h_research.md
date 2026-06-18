# File Research: sources/os/bsd/dragonflybsd/sys/sys/dmsg.h

DragonFly DMSG mesh/cluster protocol and kernel I/O communication state header, used by HAMMER2 and block-device clustering paths.

Key responsibilities:
- Documents mesh connection, SPAN advertisement/relay, stacked transactions, message state flags, abort semantics, header alignment, inline/out-of-band auxiliary data, and CRC rules.
- Defines 64-byte `struct dmsg_hdr` with magic/endian, salt, msgid, circuit, link verifier, encoded command/flags/size, aux CRC/bytes/descriptor, error, and header CRC.
- Defines protocol limits for header, aux data, and ring buffer sizing.
- Defines transaction flags, protocol IDs for link/debug/HAMMER2/block/VOP, command masks, alignment helpers, and command constructors.
- Defines link-layer commands for PAD, PING, AUTH, CONN, SPAN, and ERROR.
- Defines link connection and span structures with media/peer/PFS UUIDs, masks, type/version/status, distance/rnss, media block info, and labels.
- Defines debug shell command and block protocol commands for open/close/read/write/flush/freeblks/error with associated request/response structures.
- Defines general DMSG error constants and `union dmsg_any` for maximum-size message storage.
- Under kernel structures, defines transactional state, message, aux data, and `kdmsg_iocom` stream controller with root state, state trees, message queue, callbacks, auto connection/span state, and helper thread fields.
- Declares kernel DMSG iocom lifecycle, reconnect, auto-initiate, drain, allocation, write, reply/result, aux detach/free functions.

Dependencies:
- Includes types and uuid; kernel structures include tree and thread.
- Uses RB trees, TAILQs, locks, file descriptors, kernel threads, malloc types, and subsystem-specific pointers such as HAMMER2 and block-device state.

Notable risks:
- All extended headers must be 64-byte aligned; command encoding includes structure size and must match actual struct layout.
- Transaction lifecycle is complex: both sides create/delete, stacked child transactions must abort/terminate correctly, and relays translate ids/circuits.
- CRC calculation has special handling for `hdr_crc` being treated as zero.
- Header comments note auth is often omitted, so transport and endpoint trust assumptions must be reviewed in callers.
