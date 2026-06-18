# sources/storage-engines/tikv/components/test_pd/src/mocker/incompatible.rs

## Purpose
This mocker simulates an incompatible PD version for batch split requests.

## Important APIs And Functions
`Incompatible` implements `PdMocker::ask_batch_split` and returns an `AskBatchSplitResponse` whose header contains `ErrorType::IncompatibleVersion`.

## Control Flow, State, And Integration Points
The mocker is stateless and overrides only `ask_batch_split`; other RPCs can fall back to the default service. It is used through the generic mock server to exercise client behavior when PD lacks or rejects a feature.

## Risks And Test Signals
Because the method returns an OK gRPC response with a PD header error, tests should verify header-error interpretation rather than transport failure handling. This mocker is narrow and should not be used to simulate general version negotiation.
