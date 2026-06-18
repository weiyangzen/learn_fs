# File Research: sources/os/plan9/9front/sys/src/9/port/devaudio.c

Purpose: generic audio device front-end `#A`, dispatching to registered hardware drivers through `Audio` callbacks.

Exposed interface: directory with `audio`, `audioctl`, `audiostat`, and `volume`. Attach spec selects controller number. `audio` is bidirectional sample I/O, `audioctl` writes hardware control commands, `audiostat` reads status, and `volume` reads/writes mixer volume text.

Core implementation: `addaudiocard` registers probe functions; `audioreset` probes all registered cards and builds the `audiodevs` list. Each Chan has an `Audiochan` aux structure holding the selected `Audio`, an owner Chan, and a reusable text buffer. `audioopen` enforces one reader and one writer for `Qaudio` with separate refs. `audioread`/`audiowrite` dispatch to hardware callbacks under the per-channel qlock.

Helpers: `genaudiovolread` serializes volume tables to text, translating hardware ranges to percentages. `genaudiovolwrite` parses volume writes, supports defaulting bare values to `master`, accepts optional `in`/`out`, clamps percentages, and calls the driver setter.

Dependencies: `audioif.h` driver contract and Plan 9 device helpers.

Research notes: most policy is in the generic open/exclusive-access layer and volume parser. Hardware-specific correctness depends on callback implementations; this file assumes callbacks tolerate serialized access via `Audiochan` qlock.
