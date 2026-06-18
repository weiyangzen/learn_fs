# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/il.c

This module decodes Plan 9’s IL protocol header. It supports filters for source port, destination port, and either port.

The mux table maps well-known Plan 9 service ports such as exportfs, 9fs, cpu, and related services to `ninep`. `p_seprint` prints source/destination ports, packet type, id, ack, special byte, checksum, and length, then demuxes by either port.

Packet type names include Sync, Data, Dataquery, Ack, Query, State, and Close.
