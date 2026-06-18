# sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/downloader/__init__.py

## Purpose
Package marker for immutable downloader implementation modules.

## Important APIs, Types, And Functions
No public symbols are defined or re-exported. The docstring only notes Python 3 porting.

## Control Flow
No runtime control flow.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Supports package imports for `common`, `fetcher`, `finder`, `node`, `segmentation`, `share`, and `status`.

## Risks And Edge Cases
Adding imports here would change import-time behavior for the downloader package and may introduce dependency cycles because downloader modules already have mutual local imports.

## Test Signals
No direct tests; package import is covered by downloader and filenode tests.
