# File Research: sources/os/plan9/9front/sys/src/lib9p/fid.c

## Read Status
Complete: 81 lines read.

## Purpose
Implements fid pool allocation, lookup, reference management, and removal for lib9p servers.

## Main Responsibilities
- Allocate `Fidpool` objects backed by `Intmap`.
- Allocate new `Fid` objects and insert them by numeric fid.
- Look up fids while incrementing references.
- Remove fids from the pool.
- Close fids and release associated resources.

## Important Functions
- `allocfidpool`, `freefidpool`: create and destroy fid maps.
- `allocfid`: allocate a fid, initialize `omode = -1`, and insert it uniquely.
- `lookupfid`: find a fid by id.
- `removefid`: delete a fid mapping and return the fid.
- `closefid`: decrements reference count and frees directory readers, files, uid strings, and custom destroy state.

## Dependencies and Interactions
- Uses `Intmap` from `intmap.c` with `incfidref` as the lookup reference hook.
- Calls `closedirfile` and `closefile` for tree-backed fids.
- Optional `pool->destroy` hook lets servers clean custom fid state.
