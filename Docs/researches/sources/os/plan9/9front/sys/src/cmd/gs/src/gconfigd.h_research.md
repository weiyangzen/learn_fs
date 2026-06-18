# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gconfigd.h

## Scope

Generated Ghostscript directory, library, revision, and startup configuration.

## Key Behavior

- Sets default library path to `/sys/lib/ghostscript:/sys/lib/ghostscript/font:/sys/lib/postscript/font`.
- Sets an empty cache directory and `SEARCH_HERE_FIRST`.
- Defines documentation directory, init file name, revision number `853`, and revision date `20051020`.

## Dependencies

Consumed by Ghostscript platform/config headers and startup path logic.

## Risks And Invariants

- Paths are Plan 9 / 9front specific.
- Revision constants describe the bundled Ghostscript source snapshot.
