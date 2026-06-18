# File Research: sources/os/plan9/plan9/sys/src/lib9p/fid.c

This file manages lib9p fid allocation, lookup, reference counting, removal, and destruction.

Key behavior:
- `allocfidpool` creates an integer map whose lookup callback increments fid references.
- `allocfid` creates a `Fid`, initializes `fid`, `omode = -1`, and inserts it into the pool only if the key is unused.
- `lookupfid` returns a referenced fid by numeric id.
- `removefid` deletes a fid from the pool map and returns the referenced object.
- `closefid` releases directory-read state, calls the pool destroy hook, closes attached `File`, frees uid, and frees the fid when the refcount reaches zero.
- `freefidpool` frees the map and applies the configured fid destroy hook.

Important dependencies:
- Uses `Intmap` from `intmap.c`.
- Uses `closedirfile` and `closefile` for tree-backed fids.

Notable details:
- `allocfid` takes two references: one for the map and one for the caller/request.
- Duplicate fid insertion backs out both references and returns `nil`.
