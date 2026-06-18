# sources/storage-engines/tikv/components/test_pd/src/mocker/bootstrap.rs

## Purpose
This mocker simulates a PD server that reports an already-bootstrapped cluster when bootstrap is attempted.

## Important APIs And Functions
`AlreadyBootstrapped` implements `PdMocker`. `bootstrap` returns a `BootstrapResponse` whose header contains `ErrorType::AlreadyBootstrapped`, message `"cluster is already bootstrapped"`, and the default cluster ID. `is_bootstrapped` returns a response with the default cluster ID but `bootstrapped` set to false.

## Control Flow, State, And Integration Points
The mocker is stateless and purely response-driven. It plugs into `Server::with_case` through the `PdMocker` trait, overriding only bootstrap-related RPCs while all other calls can fall back to the default service.

## Risks And Test Signals
The deliberately inconsistent `is_bootstrapped(false)` plus bootstrap error models edge cases around bootstrap races or stale client assumptions. Tests using this mocker should assert exact PD error interpretation rather than normal cluster lifecycle behavior.
