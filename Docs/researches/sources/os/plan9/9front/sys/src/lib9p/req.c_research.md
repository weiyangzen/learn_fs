# File Research: sources/os/plan9/9front/sys/src/lib9p/req.c

## Read Status
Complete: 112 lines read.

## Purpose
Implements request pool allocation, lookup, reference management, removal, and cleanup for active 9P requests.

## Main Responsibilities
- Allocate `Reqpool` objects backed by `Intmap`.
- Allocate requests by tag and reject duplicate tags.
- Look up active requests while incrementing references.
- Remove requests from the pool.
- Close requests and release all related fid, flush, stat, buffer, and custom state.

## Important Functions
- `allocreqpool`, `freereqpool`: manage request maps.
- `allocreq`: allocate and insert a request by tag.
- `lookupreq`: find an active request by tag.
- `removereq`: remove an active request from the pool.
- `closereq`: release request references and free associated resources at zero refs.

## Dependencies and Interactions
- Uses `Intmap` from `intmap.c`.
- Used heavily by `srv.c` for duplicate tag detection, `Tflush`, and response cleanup.
- Optional `pool->destroy` hook allows server-specific request cleanup.
