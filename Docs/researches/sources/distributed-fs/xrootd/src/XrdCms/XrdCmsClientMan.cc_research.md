# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsClientMan.cc

## Purpose
Implements a persistent client-side connection to one CMS manager, including login, request sending, response receiving, delayed asynchronous replies, status updates, and reconnect/backoff behavior.

## Important APIs, Types, and Functions
Defines static buffer pool, network pointer, debug/config state, and mutex. Implements constructor/destructor, `delayResp()`, two `Send()` overloads, `Start()`, `whatsUp()`, and private `Hookup()`, `Receive()`, `relayResp()`, `chkStatus()`, and `setStatus()`.

## Control Flow
`Start()` loops forever: connect/login through `Hookup()`, receive CMS headers and payloads, route async responses to `relayResp()`, process status updates, or pass regular replies to `XrdCmsClientMsg::Reply()`. On disconnect it closes the link, marks the manager inactive/suspended, logs, sleeps, and reconnects. `Send()` writes requests only while active. `delayResp()` converts wait-response IDs into delayed response objects.

## State and Persistence Behavior
Per-manager state includes host/prefix, port, link, active/silent/suspend counters, instance number, manager mask, reconnect delay, wait/backoff timing, response queue, network buffer, and last update/timeout timestamps. State is protected by `myData` and static `manMutex` for global debug bits. No durable persistence.

## Dependencies and Integration Points
Depends on CMS login, client message table, responses, trace, XrdInet/XrdLink, SFS return codes, timers, and error reporting. Integrates with manager selection code via linked `Next` and mask/status APIs.

## Risks and Edge Cases
The constructor uses `1 << Instance++` into `manMask`; many managers can overflow an `int`. `maxMsgID` is not initialized in the constructor in the read source. `Receive()` allows resizing only for `kYR_data`; excessive other payloads are logged and treated as failure. Silent manager detection closes links after configured no-response thresholds.

## Test Signals
Tests should cover connection/login retries, suspended status changes, send failure instance bumping, wait-response synchronization, delayed async response delivery, no-response backoff/delay calculation, payload sizing, and reconnect cleanup.
