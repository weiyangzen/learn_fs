# sources/storage-engines/tikv/components/test_pd/src/mocker/split.rs

## Purpose
This mocker simulates PD membership responses with changing cluster IDs, mainly for split-brain or cluster-ID consistency tests.

## Important APIs, Types, And Functions
`Split` owns a mutex-protected optional `Inner` containing response variants and a current index. `set_endpoints` builds members from server endpoints and precomputes one `GetMembersResponse` per endpoint. Each response has a distinct cluster ID starting at one and uses the first member as leader. `get_members` increments the index and returns the next response cyclically.

## Control Flow And State
The mocker is initialized by `set_endpoints` after server binding. Every `get_members` call advances state, so clients observe rotating cluster IDs across membership refreshes.

## Persistence And Integration Points
State is in-memory and plugged into the PD mock server through `PdMocker`. It uses PD membership protobufs only.

## Risks And Test Signals
`get_members` unwraps `inner`, so the server must call `set_endpoints` before requests arrive. Cluster-ID rotation is artificial and should be used only for tests that intentionally validate client handling of inconsistent PD membership responses.
