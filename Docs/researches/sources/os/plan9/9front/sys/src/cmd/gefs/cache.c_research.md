# File Research: sources/os/plan9/9front/sys/src/cmd/gefs/cache.c

## Purpose
Implements GEFS block cache hash lookup and LRU reuse.

## Key Elements
Maintains doubly linked LRU head/tail, moves unreferenced blocks to top or bottom, inserts blocks into hash buckets by address, removes cached entries, looks up and holds cached blocks, and plucks the least-recently-used unreferenced block for reuse after uncaching and clearing bookkeeping fields.

## Dependencies
Uses global `fs` cache state, GEFS block flags/refcounts, hash helper `ihash`, tracing/assertion helpers, and Plan 9 locking/rendezvous.

## Behavior/Risks
All cache hash and LRU mutations share `fs->lrulk`. Freed blocks are placed at the LRU bottom for earlier reuse. `cachepluck` sleeps until a reusable block exists and asserts the chosen block is unreferenced and not static.
