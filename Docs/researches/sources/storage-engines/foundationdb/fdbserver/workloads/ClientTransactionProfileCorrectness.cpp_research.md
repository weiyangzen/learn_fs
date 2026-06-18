# sources/storage-engines/foundationdb/fdbserver/workloads/ClientTransactionProfileCorrectness.cpp

## Purpose
`ClientTransactionProfileCorrectness.cpp` defines a workload that validates serialized transaction profiling entries stored in client latency info. It disables sampling before check, reads all flushed profiling chunks, reconstructs multi-chunk transaction entries, and parses protocol-version-specific event payloads to verify format sanity.

## Important APIs, Types, And Functions
The file defines parser functions for `FdbClientLogEvents` event variants, `ClientLogEventsParser::ParserBase`, `Parser_V1`, `Parser_V2`, `Parser_V3`, and `ParserFactory`. Top-level helpers include `checkTxInfoEntryFormat`, `getNumChunks`, `getChunkNum`, `getTrId`, `checkTxInfoEntriesFormat`, `changeProfilingParameters`, and `_check`. It uses `GlobalConfig`, `Tuple`, `BinaryReader`, `BinaryWriter`, and system key transaction options.

## Control Flow
Client 0 sets `csi_status_delay` and writes profiling sample rate/size limit in `setup`. `check` on client 0 first sets sample rate to zero, waits for `CSI_STATUS_DELAY`, reads the client latency counter, scans all `client_latency` entries in batches, computes total stored byte size, and calls `checkTxInfoEntriesFormat`. Single-chunk entries are parsed directly; multi-chunk entries are grouped by transaction id, concatenated in chunk order, and parsed when the final chunk arrives. Missing or out-of-order chunks are logged and discarded.

## State And Persistence
The workload changes global profiling configuration and reads persistent client latency info/counter keys under `fdbClientInfoPrefixRange`. It does not clear profiling entries. Chunk assembly is in-memory during the check.

## Dependencies And Integration Points
It depends on the exact client latency key layout, event serialization protocol versions, global config writes, client status flush timing, and `CLIENT_KNOBS` limits for value sizes, key sizes, transaction sizes, and status delay.

## Risks
Hard-coded protocol version thresholds and parser mappings must be maintained when event wire formats evolve. The counter/content-size consistency check is present but commented out, so size accounting regressions may not fail this workload. Multi-chunk entries can be legitimately missed during deletion/flush races; the workload tolerates and discards incomplete entries, which prevents false failures but can hide coverage gaps.

## Test Signals
Traces include `ClientTransactionProfilingSetup`, `ClientTransactionProfilingUnknownEvent`, `ClientTransactionProfilingSomeChunksMissing`, `ClientTransactionProfilingChunksMissing`, `ClientTransactionProfilingCtrval`, and `ClientTransactionProfilingContentsSize`. `check` returns false only if parsing encounters an unknown event or invalid entry format.
