# sources/user-network-fs/samba/source3/smbd/notifyd/test_notifyd.c

## Purpose
This file registers smb-torture tests for notifyd. It validates basic trigger delivery and that notify registrations appear in and disappear from notifyd's database.

## Important APIs, Types, and Functions
`fcn_test_send()`, `fcn_test_done()`, `fcn_test_recv()`, and `fcn_test()` form an async wrapper that registers a wait and sends one trigger. `test_notifyd_trigger1()` checks delivery. `notifyd_have_fn()`, `notifyd_have_self()`, and `test_notifyd_dbtest1()` inspect database membership via `notify_walk()`. `torture_notifyd_init()` registers the suite and two simple tests.

## Control Flow
`test_notifyd_trigger1()` loads Samba config, creates messaging, finds `"notify-daemon"`, registers interest in `/home` with all filters, triggers `/home/foo`, and asserts that `fcn_wait_recv()` observed an event. `fcn_test_done()` marks `got_trigger` on the first event and cancels the underlying wait request to finish cleanly. `test_notifyd_dbtest1()` starts a wait on `/x`, uses `notify_walk()` to assert the current messaging server id is present, cancels the request, waits for cancellation, then asserts the server id is absent.

## State and Persistence
Test state is talloc/tevent scoped. `struct fcn_test_state` tracks the nested wait request and whether a trigger was seen. No durable files are written.

## Dependencies and Integration Points
The tests depend on `fcn_wait`, `notifyd_db`, Samba messaging, server-id db, torture framework, loadparm, and smbtorture module registration. They require a running notifyd registered in the messaging names db.

## Risks and Edge Cases
The tests use broad `UINT32_MAX` filters, so they do not validate precise filter/subdir filtering. They assume `/home`-style absolute paths and a live notify daemon. They do not exercise inotify kernel events, CTDB replication, malformed messages, or multiple clients on the same path.

## Test Signals
The suite name is `notifyd` with cases `trigger1` and `dbtest1`. Passing tests signal that local messaging, basic path ancestor matching, private-data delivery, `notify_walk()` parsing, and delete-on-cancel work for simple cases.
