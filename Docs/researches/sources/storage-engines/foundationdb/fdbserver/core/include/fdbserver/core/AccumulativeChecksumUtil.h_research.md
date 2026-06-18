# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/AccumulativeChecksumUtil.h

## sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/AccumulativeChecksumUtil.h

Purpose: declares utilities for attaching and validating accumulative checksums on mutation streams, primarily between commit proxies and storage servers.

Important APIs/types: constants `invalidAccumulativeChecksumIndex`, `resolverAccumulativeChecksumIndex`, `initialAccumulativeChecksum`; inline helpers `getCommitProxyAccumulativeChecksumIndex`, `calculateAccumulativeChecksum`, `tagSupportAccumulativeChecksum`, `aggregateAcs`; class `AccumulativeChecksumBuilder`; overloads of `updateMutationWithAcsAndAddMutationToAcsBuilder`; and class `AccumulativeChecksumValidator`.

Control flow and state: checksum indexes reserve commit-proxy indexes ending in `1`, while the resolver has index `2`. Accumulation is XOR of mutation checksums. Supported tags currently require non-negative locality. The builder tracks current version and an ACS table per tag, updates tag state on tag assignment or mutation tagging, and exposes the table for read-only inspection. The validator buffers non-ACS mutations, consumes the buffer when an ACS mutation arrives, compares generated state to carried state, restores persisted ACS state, clears stale buffers, and exposes counters for metrics.

State and persistence behavior: builder/validator state is in-memory, but validator `processAccumulativeChecksum` returns an `AccumulativeChecksumState` intended to be persisted in storage server private data. Restore overwrites table state from persisted data.

Dependencies and integration: depends on client ACS types, commit transaction mutations, system tags, versions, epochs, and storage metrics counters. It integrates with commit proxy mutation generation and storage server pull/apply paths.

Risks and tests: every aggregated mutation must carry a checksum. Missing ACS mutations leave buffered data until `clearCache`, trading bounded memory for later mismatch detection. Tests should cover multiple tags, tag reassignment, persisted restore, missing ACS mutation, unsupported tags, counter clearing, and XOR compatibility.
