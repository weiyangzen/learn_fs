# sources/object-store/daos/src/vos/vos_query.c

## Purpose
`vos_query.c` implements object key queries for minimum/maximum dkey, akey, recx, and max-write epoch. It traverses object, dkey, akey, and evtree state under timestamp/ilog visibility constraints, with special handling for erasure-coded parity extents.

## Important APIs, Types, And Functions
The main API is `vos_obj_query_key`. `struct open_query` carries the held object, timestamp set, epoch bounds, punch record, ilog info, tree roots/handles, anchors, EC stripe/cell sizing, flags, and pool/container handles. Helpers include `check_key`, `find_key`, `query_normal_recx`, `query_ec_recx`, `find_answer`, `open_and_query_key`, and overlap adjustment helpers.

## Control Flow
The public query validates flags, allocates an `open_query`, creates timestamp tracking, holds a visible object, and optionally returns `vo_max_write`. For key queries it opens the dkey tree, finds the next/previous visible integer key when requested, then opens the akey tree or flat dkey value tree, and finally queries recx data from evtree. If a selected dkey/akey has no valid descendant, the code restores timestamp snapshots and continues to the next candidate.

## State And Persistence
The query is read-only but mutates runtime timestamp sets and ilog fetch state. It updates effective epoch ranges and punch records as it descends so child visibility is constrained by parent punches. It closes any open btree/evtree handles before release and records read dependencies so callers can restart on uncertainty.

## Dependencies And Integration Points
This module depends on object cache holds, VOS ilog/timestamp APIs, dbtree iteration, evtree visibility filters, DAOS object type helpers for integer-key validation, checksum/media address structures, DTX in-progress detection, and EC layout constants such as `DAOS_EC_PARITY_BIT`.

## Risks
Risks include incorrect timestamp restore when skipping invalid descendants, EC parity/data extent comparison errors, off-by-one overlap trimming, assuming integer dkey/akey types, and returning stale answers under uncertain DTX state. EC mode maps parity extents to equivalent data ranges, so stripe/cell size inputs must be valid.

## Test Signals
Tests should cover max/min dkey, akey, and recx, max-write-only query, non-integer key rejection, flat dkey objects, holes and punched entries, DTX in-progress restart paths, descendant skip loops, EC parity-only/data-only/overlap cases, and cleanup of open handles on every error path.
