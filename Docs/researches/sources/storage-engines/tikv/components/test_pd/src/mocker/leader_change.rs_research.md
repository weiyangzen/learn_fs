# sources/storage-engines/tikv/components/test_pd/src/mocker/leader_change.rs

## Purpose
This mocker simulates PD leader changes and a dead PD member so clients can test reconnect and leader-refresh behavior.

## Important APIs, Types, And Functions
`LeaderChange` owns a mutex-protected `Inner` containing prebuilt `GetMembersResponse`s and a `Roulette` with last-change timestamp and index. `get_leader_interval` returns the fixed two-second leader interval. `set_endpoints` builds a PD member list from bound server endpoints, appends a dead member at `127.0.0.1:65534`, and creates one response per live endpoint with a different leader. `get_members` rotates leader after the interval and returns `"not leader"` once when rotating. `get_region_by_id` also errors after the interval to force retry.

## Control Flow And State
State advances with wall-clock time. Before the interval expires, calls return the current response. Once expired, the index increments, timestamp resets, and the first call gets an error so the client updates its connection.

## Persistence And Integration Points
This is in-memory test state integrated through `PdMocker`. It uses PD protobuf `Member`/`GetMembersResponse` and the mock server's endpoint injection.

## Risks And Test Signals
Tests are timing-sensitive because behavior changes after two seconds. `get_members` indexes `inner.resps` and assumes `set_endpoints` has run before use. The dead member checks client robustness against unreachable PD addresses.
