# sources/object-store/minio-mc/cmd/admin-heal-ui.go

## Purpose
Provides the live, quiet, and JSON display engine for `mc admin heal` task progress. It aggregates heal result records into statistics and terminal UI output.

## Important APIs, types, and functions
Important symbols are `getHColCode`, `uiData`, `updateStats`, `getProgress`, `getPercentsNBars`, `printItemsQuietly`, `printItemsJSON`, `printStatsJSON`, `updateUI`, `UpdateDisplay`, `healResumeMsg`, and `DisplayAndFollowHealStatus`.

## Control flow
The follow loop repeatedly calls `AdminClient.Heal` with the stored client token, updates duration and accumulated stats from returned items, redraws the interactive UI unless quiet or JSON is selected, and exits on `finished`, `stopped`, or global context cancellation.

## State and persistence behavior
`uiData` stores transient counters: bytes scanned, objects/items scanned and healed, counts by online drives, health-color counts, last item, and elapsed duration. Persistent healing state remains on the server and is referenced by the client token.

## Dependencies and integration points
The file integrates `madmin.HealTaskStatus`, heal result helper methods, cursor animation, console rewind/table/color APIs, `colorjson`, humanized sizes, and the global JSON/quiet flags.

## Risks and edge cases
Color classification rejects parity outside 1..8 or surplus above parity. `getProgress` manually computes binary units and assumes an in-range magnitude. Display rewinds a fixed number of lines, so terminal layout changes are fragile. Context cancellation returns a resume hint as an error.

## Test signals
Tests should cover health-color table boundaries, stats accumulation for healed and non-healed items, JSON record shape, quiet output error fallback, final summary output, stopped task error propagation, and context cancellation resume text.
