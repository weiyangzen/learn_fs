# sources/storage-engines/foundationdb/fdbserver/workloads/GetRangeStream.cpp

## Purpose
Small performance and API comparison workload for reading a key range either through repeated `getRange` calls or through the streaming `getRangeStream` interface.

## Important APIs, types, and functions
`GetRangeStream` derives from `TestWorkload` and exposes options `useGetRange`, `begin`, `end`, and `printKVPairs`. It records `BytesRead`. `fdbClientGetRange` uses `Transaction::getRange` with `CLIENT_KNOBS->REPLY_BYTE_LIMIT`; `fdbClientStream` uses `Transaction::getRangeStream` into a `PromiseStream<Standalone<RangeResultRef>>`; `logThroughput` prints one-second byte rates.

## Control flow
Only client 0 runs. The workload starts a throughput logger and repeatedly reads from `begin` to `end`. The getRange mode advances `next` to `keyAfter(range.back().key)` while `range.more` is true. The stream mode consumes range batches from the promise stream until `end_of_stream`, updating `next` after non-empty chunks and retrying via `tx.onError` for other transaction errors.

## State and persistence behavior
The workload does not write database state. Runtime state is limited to the current continuation key and the byte counter. It reuses a single transaction object across retries, relying on `onError` reset semantics.

## Dependencies and integration points
Integrates with native API range reads, streaming range plumbing, Flow `PromiseStream`, tester workload registration, and normal key boundaries from tester helpers.

## Risks and test signals
Because `check` always returns true, this is primarily an operational metric workload. Risks are infinite streaming loops if stream termination changes, noisy stdout when `printKVPairs` is true, and stale transaction behavior around retries. The main signal is the `BytesRead` perf metric plus optional throughput prints.
