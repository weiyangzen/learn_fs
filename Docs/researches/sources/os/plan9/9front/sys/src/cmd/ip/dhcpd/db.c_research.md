# File Research: sources/os/plan9/9front/sys/src/cmd/ip/dhcpd/db.c

Lease database for `dhcpd`. Maintains an in-memory binding cache backed by exclusive files under `/lib/ndb/dhcp`, with each lease file storing expiration time and bound client ID.

Core operations include client ID formatting, binding initialization over configured pools, stale-file synchronization, old-binding reuse, free-binding search, ICMP conflict probing, offer creation, lease commit, and release.

The file-backed locking model lets multiple DHCP server processes coordinate. Existing lease files win over cache state whenever qid version changes.
