# sources/storage-engines/pebble/internal/manifest/doc.go

## Purpose
This package documentation records the correctness argument for organizing L0 into sublevels. It explains why ordering L0 files by sequence-number-derived metadata can preserve read semantics and how L0-to-base and intra-L0 compactions can safely choose triangular sets of files.

## Important APIs, Types, And Functions
There are no Go declarations beyond `package manifest`. The important content is the proof sketch: claims about file-add history, key sequence ordering, largest sequence number ordering, equivalence between simple add-order stacks and sequence-number stacks, and safety arguments for sublevel compactions.

## Control Flow
The document progresses from historical file addition order, through two core claims about overlapping keys and largest sequence numbers, to sublevel organization. It then discusses L0-to-Lbase compactions as bottom triangles and intra-L0 compactions as inverted top triangles, including the role of `earliest-unflushed-seq-num` and output-file ordering.

## State, Persistence, And Side Effects
The file has no runtime state or side effects. Its persistence role is architectural: it captures assumptions that the implementation in `l0_sublevels.go`, compaction picking, ingest/flush ordering, and sequence-number assignment rely on.

## Dependencies And Integration Points
The proof references Pebble ingest/flush behavior, memtable flush ordering, atomic ingests, commit pipeline sequencing, L0 sublevels, Lbase compactions, and historical GitHub issues. It is the design companion to `l0_sublevels.go` and to compaction picker logic that enforces triangular selection.

## Risks And Edge Cases
The proof is explicitly marked incomplete in places, especially for the hybrid real LSM where compactions remove files from L0 at arbitrary times. TODOs call out missing details for hybrid correctness and L0-to-Lbase compactions. If ingest/flush sequencing or output ordering changes, this proof must be revisited.

## Test Signals
There are no tests for the document itself. Its claims are indirectly tested by L0 sublevel tests, compaction picker tests, version/invariant checks, and read correctness tests elsewhere in Pebble.
