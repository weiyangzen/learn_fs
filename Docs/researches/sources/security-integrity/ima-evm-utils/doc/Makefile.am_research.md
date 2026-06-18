# sources/security-integrity/ima-evm-utils/doc/Makefile.am

## Purpose
Doc subdirectory Automake entry point.

## Important APIs, Types, And Functions
- `SUBDIRS = sf` delegates all doc build work to the `sf` folder.

## Control Flow
When top-level Automake includes `doc`, recursive make descends into `doc/sf`.

## State And Persistence
No direct generated state is defined in this file.

## Dependencies And Integration Points
Depends on top-level `HAVE_PANDOC` conditional and the child `doc/sf/Makefile.am`.

## Risks And Edge Cases
The file is intentionally minimal; missing child Makefile generation would make doc builds fail.

## Test Signals
Signal is recursive make entering and completing `doc/sf`.
