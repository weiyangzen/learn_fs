# File Research: sources/local-fs/xfsprogs/db/btheight.c

Implements `btheight`, a geometry estimator for btree heights and block counts. It knows built-in btree types (`bnobt`, `cntbt`, `inobt`, `finobt`, `bmapbt`, `refcountbt`, `rmapbt`, `rtrmapbt`, `rtrefcountbt`) via libxfs max-level and max-record callbacks, and also accepts raw geometry strings of the form `record_bytes:key_bytes:ptr_bytes:header_type`.

The command parses record count, optional block size, and reporting mode: best case, average case, worst case, or absolute maximum height. It validates block-size and geometry underflow cases, computes leaf/node records per block, then repeatedly folds records into parent blocks to print per-level and total block counts. It is analytical only and does not inspect or mutate on-disk btrees.
