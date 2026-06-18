# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ospf.c

This snoopy module formats OSPF packets and several OSPF payload types. It defines OSPF packet headers, hello packets, database description packets, link-state advertisement headers, link-state update formats, and link-state acknowledgements.

Key behavior:
- Validates the 24-byte OSPF header and packet length before decoding.
- Prints version, type, router ID, area, checksum, and authentication description.
- Handles hello, database description, link-state update, and link-state ack packets specially.
- Dumps unknown or request payloads as hex, capped to 64 bytes.
- Terminal protocol: no filters or mux table.

Research notes:
- `ospfauth()` appears to switch on `ospf->type` rather than `autype`, so authentication text may be inaccurate.
- Link-state update decoding chooses the union interpretation from the first LSA type and does not deeply validate per-LSA lengths.
