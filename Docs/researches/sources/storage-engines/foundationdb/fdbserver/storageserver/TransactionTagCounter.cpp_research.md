# sources/storage-engines/foundationdb/fdbserver/storageserver/TransactionTagCounter.cpp

Purpose: implements per-storage-server read request tag accounting to identify busiest read tags for ratekeeper auto-throttling.

Important APIs and functions: `TransactionTagCounterImpl::addRequest` converts read bytes to operation cost, scales tagged costs by `READ_TAG_SAMPLE_RATE`, and accumulates interval totals. `startNewInterval` computes elapsed time, selects top K tags above a minimum rate with a priority queue, stores them as `BusyTagInfo`, emits `BusiestReadTag` and `BusyReadTag` traces, and resets interval state. Public `TransactionTagCounter` forwards constructor, destructor, `addRequest`, `startNewInterval`, and `getBusiestTags`. Local tests check max-tag and min-rate filtering.

Control flow, state, and persistence: state is in-memory interval cost maps, total cost, previous busiest tags, and TraceEvent cache holder. There is no durable persistence.

Dependencies and integration: depends on transaction tags, `getReadOperationCost`, client/server knobs, Flow tracing, and the PImpl wrapper declared in `TransactionTagCounter.h`. Storage read paths feed it; ratekeeper later consumes busy tags through storage queuing metrics.

Risks and test signals: risks are sampling-rate zero handling, elapsed-time zero, arena ownership for copied tags, and top-K ordering not being sorted highest-first. Existing tests cover ignoring beyond max tags and below-min-rate tags; additional tests should cover multi-tag requests and zero sample rate.
