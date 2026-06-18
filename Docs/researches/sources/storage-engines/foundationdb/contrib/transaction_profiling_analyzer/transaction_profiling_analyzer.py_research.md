# sources/storage-engines/foundationdb/contrib/transaction_profiling_analyzer/transaction_profiling_analyzer.py

## Purpose
This Python CLI reads FoundationDB client transaction profiling samples from system keys, decodes versioned binary log events, optionally prints JSON transaction event records, and can summarize read/write hot spots and approximate key-space buckets with current shard-location annotations.

## Important APIs, Types, And Functions
Protocol constants enumerate supported client log encodings from 5.2 through 8.0. `ByteBuffer` is the binary decoder for little-endian ints, longs, doubles, booleans, length-prefixed byte strings, key ranges, and mutations. `MutationType`, `Mutation`, `KeyRange`, and the `BaseInfo` subclasses model event payloads from `FdbClientLogEvents::Event`: get version, get, get range, commit, and error variants. `ClientTransactionInfo` decodes one complete transaction sample and filters event types. `TransactionInfoLoader` scans `\xff\x02/fdbClientInfo/client_latency/`, reassembles multi-chunk values, and maps timestamp arguments through Timekeeper. `ReadCounter`, `WriteCounter`, and `ShardFinder` compute top operations, bucket boundaries, and storage-server address metadata. `main` owns CLI parsing and output.

## Control Flow
The CLI builds a `type_filter`, chooses read/write counters, parses required start/end times, opens the FDB database, and iterates `TransactionInfoLoader.fetch_transaction_info`. The loader computes start/end key selectors from Timekeeper versions when timestamps are supplied, scans system keys in snapshot read-lock-aware transactions, decodes single-chunk values directly, buffers ordered multi-chunk samples by transaction id, and yields decoded `ClientTransactionInfo` objects. Output either prints JSON per transaction or aggregates into counters, then reports top keys/ranges and key-space buckets with optional shard/address filters.

## State And Persistence
The script does not mutate FoundationDB. It reads system keys and current locality metadata. In-process state includes the multi-chunk cache capped by `max_num_chunks_to_store`, counters for reads/writes, a shard-address future cache, and a file logger at `transaction_profiling_analyzer.log`.

## Dependencies And Integration Points
Required dependencies are Python 3 and FDB Python bindings. Optional `dateparser` parses human time strings, and `sortedcontainers` enables read-density counting. The binary decoding must stay synchronized with FoundationDB `fdbclient/ClientLogEvents.h` and protocol-version layout changes. It uses `fdb.api_version(520)`, `fdb.impl.strinc`, `fdb.locality`, key selectors, transaction options for system-key and lock-aware reads, and `fdb.tuple` for Timekeeper values.

## Risks
The code is sensitive to binary protocol drift; unsupported protocol versions and malformed values are counted invalid and skipped. Chunk cache eviction can discard large or out-of-order multi-chunk samples. `assert` statements validate key parsing and chunk ordering, which can terminate optimized/debug runs differently. `full_output = args.full_output or (args.num_buckets is not None)` means the default bucket count makes commit mutations load even without `--full-output`. `print_top` assumes shard addresses are present when printing top results with shard finder. Current shard locations may not match historical operation locations, which the CLI warns about.

## Test Signals
The subset test file does not currently import this module successfully because it imports `RangeCounter`, which is not defined here. Missing tests include ByteBuffer decoding for each supported protocol, chunk reassembly and eviction, Timekeeper range selection, filter behavior, JSON output, top/bucket calculations, and CLI argument validation.
