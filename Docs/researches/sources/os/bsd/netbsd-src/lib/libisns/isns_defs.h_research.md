# File Research: sources/os/bsd/netbsd-src/lib/libisns/isns_defs.h

Protocol definition header for iSNS.

Defines:
- iSNS function IDs for registration, query, deregistration, SCN, discovery domain operations, ESI, heartbeat, iFCP requests, and response IDs.
- iSNS tag type IDs for entity, portal, iSCSI node, portal group, Fibre Channel, switch, discovery domain set, and discovery domain attributes.
- PDU header flag constants for first/last PDU, replace registration, authentication, sender server, and sender client.

This is the public constants surface for constructing and interpreting iSNS PDUs/TLVs.
