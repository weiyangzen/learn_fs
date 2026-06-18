<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/arenaskl/node.go -->
# sources/storage-engines/pebble/internal/arenaskl/node.go

## Purpose
This file defines the arena-resident skiplist node layout and node allocation helpers.

## Important APIs, Types, And Functions
`MaxNodeSize` computes worst-case memory. `links` stores atomic next/prev offsets. `node` stores key offset/size, internal trailer, value size, padding, and a tower. `newNode`, `newRawNode`, `getKeyBytes`, `getValue`, and CAS offset methods manage node content and links.

## Control Flow
`newNode` validates height and key/value sizes, allocates raw node memory, stores the trailer, and copies key/value bytes. `newRawNode` truncates unused tower memory based on height and asks the arena to reserve overflow bytes.

## State And Persistence Behavior
Nodes live in arena memory and store offsets rather than Go pointers, reducing GC interaction. Keys and values are immutable after insertion.

## Dependencies And Integration Points
It depends on `base.InternalKey`, atomics, `unsafe`-compatible arena allocation, and Cockroach errors. `skl.go` links nodes concurrently.

## Risks And Edge Cases
The node struct must not contain heap pointers before arena type-casting. Size overflow, incorrect tower truncation, or bad offset CAS would corrupt skiplist order or crash under the race detector.

## Test Signals
`skl_test.go` checks no-pointer layout and ordering; `race_test.go` checks arena-boundary node allocation.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/arenaskl/node.go -->
