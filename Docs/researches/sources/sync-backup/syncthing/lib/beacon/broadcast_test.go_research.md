# sources/sync-backup/syncthing/lib/beacon/broadcast_test.go

Purpose: Unit test for IPv4 broadcast address calculation.

Important APIs/types/functions: `addrToBcast` lists CIDR inputs and expected broadcast CIDRs. `TestBroadcastAddr` parses each CIDR, calls `bcast`, and compares string output.

Control flow: Table-driven straight-line test.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Protects the address computation used by `writeBroadcasts`.

Risks: Does not test interface enumeration, UDP socket writes, or Android-specific filtering.

Test signals: Good signal for netmask arithmetic across /0, /22, /24, /25, and /32 cases.
