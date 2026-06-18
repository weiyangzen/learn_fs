# sources/user-network-fs/samba/source4/librpc/idl/winsrepl.idl

## Purpose

`winsrepl.idl` defines NDR descriptions for the WINS replication protocol on port 42, even though the protocol is not traditionally IDL/NDR encoded. It gives Samba generated parsers for replication PDUs.

## Important APIs And Types

The interface UUID is `915f5653-bac1-431c-97ee-9ffb34526921`. Public constant `WINS_REPLICATION_PORT` is 42. Types describe IP owner/address pairs, address lists, name types, name states, node types, bitmapped flags, owner/version ranges, replication tables, command discriminants, start/stop association messages, and wrapped packets.

`wrepl_wins_name` combines an NBT name, flags, computed group flag, version id, discriminated address data, and an unknown IPv4 field. `wrepl_replication_cmd` distinguishes table query/reply, send request/reply, update/update2, and inform/inform2. Public `wrepl_packet` is generated-size, big-endian, PAHEX flagged and includes opcode, association context, message type, switched message, and remaining padding. Public `wrepl_wrap` prefixes packet size.

## Control Flow And State

The schema models association startup, association stop, and replication message exchange. State is represented by association context, owner version ranges, command-specific tables or records, and padding retained from the wire.

## Dependencies And Integration Points

It imports `nbt.idl` and uses the NBT helper header. The generated NDR parser is used by WINS replication client/server code and by WINS admin IDL through shared name structures.

## Risks

Several fields encode observed protocol quirks, including opcode bits and nodiscriminant unions. Changing discriminants, endian flags, or computed group flag logic can break wire interoperability. `NDR_REMAINING` padding must be preserved where peers expect noncanonical bytes.

## Test Signals

Round-trip tests should use captured WINS replication packets for start association, table query/reply, send reply with unique/group/multihomed records, and stop association. Tests should verify big-endian wrapping, little-endian address-list substructure, and size calculation.
