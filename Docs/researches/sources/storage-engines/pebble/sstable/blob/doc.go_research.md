# sources/storage-engines/pebble/sstable/blob/doc.go

## Purpose
This package documentation explains the blob file format used for separated values, including value blocks, index blocks, footers, and sparse rewrites.

## Important APIs, Types, and Functions
Although it contains no executable APIs, it defines the conceptual contract for `BlockID`, `BlockValueID`, index block virtual mappings, physical offsets, value block raw-byte columns, and V1/V2 footer fields.

## Control Flow
The documented read path is: an SSTable stores a blob handle with blob file reference, block ID, and block value ID; a reader loads the blob file index block; it maps the block ID to a physical block handle; then it loads the value block and indexes into the raw-bytes column.

## State and Persistence Behavior
The documentation is the persisted-format guide. It describes a file as value blocks followed by an index block and fixed footer. Rewrites may elide unreferenced values while keeping old handles valid through virtual block mappings and empty value placeholders.

## Dependencies and Integration Points
It aligns with `handle.go`, `blocks.go`, `blob.go`, `fetcher.go`, and `rewrite.go`, and references `colblk` as the columnar encoding mechanism.

## Risks
Documentation drift would be high impact because this file explains on-disk compatibility. The TODOs around virtual-block integer interleaving and possible null bitmap indicate future format evolution considerations.

## Test Signals
The executable tests in the blob package validate the format described here through writer, reader, index block, fetcher, and rewrite behavior.
