# sources/object-store/daos/src/vos/vos_layout.h

## Purpose
`vos_layout.h` defines the durable VOS pool, container, DTX, object, key, and value formats. These structures are persisted in the backing umem/PMEM metadata and are the layout contract that runtime code in VOS opens, validates, upgrades, and mutates.

## Important APIs and Types
The file defines `VOS_POOL_LAYOUT`, durable pool version constants, release feature masks, GC bin/bag/bucket records, `struct vos_pool_ext_df`, `struct vos_pool_df`, DTX durable entries (`vos_dtx_cmt_ent_df`, `vos_dtx_act_ent_df`, `vos_dtx_blob_df`), IO stream ids, container extensions (`vos_cont_ext_df`), `struct vos_cont_df`, key record flags, `struct vos_krec_df`, `struct vos_irec_df`, `struct vos_obj_df`, and md-on-SSD phase2 `struct vos_obj_p2_df`.

## Control Flow and Usage
The header is not executable control flow, but it constrains pool/container open, object/key tree operations, DTX indexing, IO update/fetch, aggregation, GC, and layout compatibility checks. Runtime code reads pool durable format version and feature gates before using newer fields such as aggregation optimization, checksum/container extension data, dynamic roots, flat dkeys, embedded first values, and gang single values.

## State and Persistence
Pool state includes magic/version, compatibility flags, extension offset, pool uuid, SCM/NVMe sizes, container count, dedup placeholder, container btree root, VEA free-space state, and GC bins. Container state includes uuid, object count, timestamp index, used bytes, highest aggregated epoch, object tree root, extension offset, DTX blob heads/tails, VEA hints, GC bins, and newest aggregated DTX epoch. Object/key/value state includes object id, sync and max-write epochs, known key offsets, ilogs, dkey btree root, key payload and checksum bytes, SV metadata, DTX local ids, minor epochs, payload size, EC global size, and external BIO addresses.

## Dependencies and Integration
The layout depends on DAOS btree roots, evtree roots, VOS public types, BIO addresses, VEA structures, DTX server types, and generic ilog durable roots. `vos_internal.h` wraps these durable records in runtime objects and provides accessors that compute payload, checksum, key, and data offsets. IO and iterator code assume the bitmap flags identify whether a key owns a btree, evtree, dkey role, or no-akey flat value.

## Risks and Test Signals
The largest risks are durable format incompatibility, feature use against older pools, structure padding drift, incorrect flexible-array sizing, DTX blob head/tail assumptions, GC bucket limit mismatch, and value-address interpretation across SCM, NVMe, holes, gang addresses, and md-on-SSD phase2 object buckets. Tests should include layout version compatibility, pool feature gates, DTX blob append/reindex, container extension validity bits, key/value checksum offset calculations, gang SV storage, flat-dkey records, GC bag/bin persistence, and assertions guarding contiguous DTX head/tail fields and object phase2 sizing.
