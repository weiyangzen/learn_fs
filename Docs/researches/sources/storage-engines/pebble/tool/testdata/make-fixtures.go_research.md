# Research: sources/storage-engines/pebble/tool/testdata/make-fixtures.go

## Purpose
`tool/testdata/make-fixtures.go` is a fixture generator for Pebble tool tests. It builds specialized databases used to exercise CLI behavior around external files, remote object storage metadata, synthetic prefix/suffix formats, and CockroachDB key schema formatting.

## Important APIs, Types, And Functions
`makeBrokenExternalDB` creates a database named `broken-external-db` using `FormatSyntheticPrefixSuffix`, disabled automatic compactions, and an in-memory remote storage factory. It writes a remote `foo.sst`, creates local compacted ranges, and ingests the external file with intentionally suspicious metadata such as a declared size of `123` and a broad `[a25,c19]` key range.

`makeCRSchemaDB` creates `cr-schema-db` with the CockroachDB comparer and key schema, generates deterministic random Cockroach KVs using `rand.NewPCG(1,1)`, flushes, and compacts the resulting table.

`main` runs both fixture builders.

## Control Flow
Each builder constructs Pebble options, opens an absolute-path database, writes deterministic contents, flushes and compacts to produce stable LSM structure, prints `db.DebugString`, and closes the DB. The external DB path creates a remote SST first, then introduces local data on either side of the external span before ingesting it.

## State And Persistence
The program creates or overwrites fixture DB directories relative to its working directory. It persists Pebble manifests, SSTables, local metadata, and remote in-memory object contents during execution; only the generated DB directories survive the process. `ErrorIfExists` prevents accidental overwrite of existing fixture directories.

## Dependencies And Integration Points
It depends on Pebble DB APIs, `sstable.NewWriter`, `objstorageprovider.NewRemoteWritable`, remote storage locators, and CockroachDB key-generation utilities. The generated fixtures feed `tool` datadriven tests for DB, LSM, manifest, sstable, and remote/external introspection.

## Risks And Edge Cases
Fixture determinism depends on format versions, compaction behavior, random generator stability, and key schema semantics. The external file fixture deliberately creates an unusual ingest state; if Pebble starts rejecting it or changes DebugString output, golden tests must be regenerated carefully. Because paths are absolute after `filepath.Abs`, running from the wrong directory can create fixtures in the wrong tree.

## Test Signals
Useful signals include stable `DebugString` output, expected remote object references, external file metadata visibility, and Cockroach key-schema pretty formatting. The generated data also checks that tools can inspect DBs using newer format gates and custom comparers.
