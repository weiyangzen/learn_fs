# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/dnarea.c

Maintains DNS authority areas derived from SOA records. Two global lists are used: `owned` for zones served locally and `delegated` for delegated subareas excluded from local authority.

`inmyarea()` checks whether a name is under an owned area and not under a delegated area. `addarea()` classifies SOA tuples by whether the `soa` tuple value is empty, stores a copied SOA RR, sets notify/refresh flags, and logs new areas in debug mode. `freearea()` frees area lists and their SOA copies.

`refresh_areas()` runs `zonerefreshprogram zone-name` for areas marked `needrefresh`; successful child completion clears the flag. This is used by notify handling and database reload cycles.

Risks are mostly ownership and locking: SOA records are copied under `dnlock`, and `freearea()` frees RRs while briefly holding `dnlock`. External refresh execution is synchronous per area.
