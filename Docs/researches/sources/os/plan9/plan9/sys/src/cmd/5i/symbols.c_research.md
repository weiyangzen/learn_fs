# File Research: sources/os/plan9/plan9/sys/src/cmd/5i/symbols.c

## Scope

Source, parameter, local, and stack-trace formatting for `5i`.

## Behavior

- Prints source file/line for guest PCs through Mach symbol APIs.
- Prints locals and parameters by reading guest stack memory according to symbol metadata.
- `stktrace()` walks frames from guest PC/SP until `_main`, printing function calls, parameters, source locations, and optional locals.

## Dependencies

Uses Mach symbols (`findsym`, `findlocal`, `localsym`, `fileline`, `symoff`) and guest memory reads.

## Risks And Invariants

- Stack walking assumes Plan 9 ARM frame conventions and `.frame` local metadata.
- Stops after 40 frames to avoid runaway traces.
