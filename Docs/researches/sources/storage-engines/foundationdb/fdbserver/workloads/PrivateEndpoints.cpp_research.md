## sources/storage-engines/foundationdb/fdbserver/workloads/PrivateEndpoints.cpp

`PrivateEndpoints` is an untrusted-mode workload that verifies private proxy endpoints reject unauthorized client calls. It randomly chooses GRV or commit proxy request streams that should not be callable by ordinary clients, sends default requests through either `tryGetReply` or `getReply`, and treats `unauthorized_attempt` as success.

Important APIs are `ClientDBInfo`, `GrvProxyInterface`, `CommitProxyInterface`, `RequestStream<RT, false>`, `throwErrorOr`, `error_code_unauthorized_attempt`, and `error_code_request_maybe_delivered`. Template helpers `getInterface`, `assumeFailure`, and `addTestFor` build a vector of test functions for supported private channels.

At construction, the workload adds tests for GRV proxy `waitFailure` and `getHealthMetrics`, plus commit proxy `waitFailure` and `exclusionSafetyCheckReq`. `_start` waits `startAfter`, then loops for `runFor`, selecting a random test function, racing it against the end timer, incrementing `numSuccesses` for completed expected failures, and sleeping 0.2 seconds between attempts.

There is no durable state. Runtime state is `success`, `numSuccesses`, timing options, and the function vector. Risks include default-constructed request payloads not being valid for every possible private endpoint, empty proxy lists causing the test to wait on `clientInfo->onChange`, and treating `request_maybe_delivered` as success because connection failures can mask authorization. `success` is never set false; unexpected errors assert in `_start`.

Integration points are client DB info propagation, private endpoint authorization, proxy interfaces, and the untrusted workload factory (`UntrustedMode::True`). Test signals are the `Successes` metric and trace events for expected unauthorized or maybe-delivered outcomes. A wrong error code logs `WrongErrorCode` but does not directly set failure before `assumeFailure` returns, making trace review important.
