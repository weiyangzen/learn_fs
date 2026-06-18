# sources/user-network-fs/nfs-ganesha/src/include/nlm_async.h

## Purpose
This header declares the asynchronous NLM response path. It coordinates sending NLMv4 async callbacks/results and waking waiters that are blocked waiting for a response key.

## Important APIs, Types, And Functions
It exports `nlm_async_resp_mutex` and `nlm_async_resp_cond` for response synchronization. `nlm_async_callback_init()` initializes the async callback machinery. `nlm_send_async_res_nlm4()` and `nlm_send_async_res_nlm4test()` send async responses for normal NLM results and TEST results through a `state_async_func_t` callback. `nlm_send_async()` is the generic client-side send routine taking an NLM procedure number, host/client state, argument pointer, and wait key. `nlm_signal_async_resp()` signals completion for a key.

## Control Flow
Callers initialize once, then use `nlm_send_async()` or the typed result wrappers to issue RPC messages to a `state_nlm_client_t`. The key argument is the rendezvous identity for a waiter; when a corresponding async result is observed, `nlm_signal_async_resp()` wakes waiters via the exported mutex/condition pair.

## State And Persistence
State is transient process memory: the global mutex, condition variable, host/client structures, callback function references, result storage in `nfs_res_t`, and wait keys. No persistent data is written by this layer, but its completion signals influence lock wait progress and blocked-lock grant behavior.

## Dependencies And Integration Points
The header depends on pthreads and `sal_data.h` for `state_nlm_client_t`, `state_async_func_t`, and `nfs_res_t`. It integrates with generated NLM RPC procedures from `nlm4.h`, blocked-lock handling, and NLM utility/state code that registers owners and lock entries.

## Risks And Test Signals
Risks include lost wakeups, key lifetime bugs, holding `nlm_async_resp_mutex` across slow RPC paths, mismatched callback function signatures, and double signaling. Test signals include async lock-grant callbacks, timeout/cancel paths, multi-client concurrent waits, callback init idempotence, and fault-injection of unreachable NLM peers.
