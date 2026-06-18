# File Research: sources/os/linux/linux/fs/gfs2/trans.h

## Scope

This header defines transaction reservation constants and declares the GFS2 transaction API.

## APIs And Definitions

- Reservation constants define one-block logical costs for dinodes, indirect blocks, journaled data, regular data, leaves, rgrp headers, rgrp bitmap work, xattrs, statfs, and quota.
- `gfs2_rg_blocks()` computes the rgrp transaction reservation for an allocation as either `requested + 1` for the rgrp header or the full rgrp bitmap/header length, whichever is smaller.
- Declarations expose transaction begin/end/free, metadata/data attachment, folio data-buffer attachment, and revoke add/remove.

## Dependencies And Invariants

`gfs2_rg_blocks()` assumes `ip->i_res.rs_rgd` is valid. Callers must combine these constants conservatively; under-reservation is caught later by transaction assertions and can trigger withdrawal. Data and metadata attachment require an active transaction in `current->journal_info`.
