# sources/user-network-fs/nfs-utils/support/include/xio.h

## Purpose
Declares simple file/token parsing and advisory lock helpers.

## Important APIs, Types, and Functions
`XFILE`, `xfopen()`, `xflock()`, `xfunlock()`, `xfclose()`, `xgettok()`, `xgetc()`, `xungetc()`, `xskip()`, and `xskipcomment()`.

## Control Flow
Callers open an `XFILE`, consume tokens/chars with line tracking and comment skipping, and use lock helpers around shared state files.

## State and Persistence Behavior
`XFILE` owns a FILE pointer and line counter. Lock helpers operate on external lock files.

## Dependencies and Integration Points
Used by export/rmtab parsers and etab locking.

## Risks and Edge Cases
Parsing helpers have fixed token buffer contracts; lock acquisition failures must be handled by callers.

## Test Signals
Test token parsing, line counts, comments, pushback, lock read/write modes, and close/unlock cleanup.
