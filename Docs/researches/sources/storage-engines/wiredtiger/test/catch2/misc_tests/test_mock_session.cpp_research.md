# sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_mock_session.cpp

## Purpose
Directly tests basic mock-session event-handler behavior used by many internal Catch2 tests.

## Important APIs, Types, And Functions
Uses `mock_session::build_test_mock_session`, `add_callback_message`, `get_last_message`, and the mock session's `WT_EVENT_HANDLER` callbacks `handle_error` and `handle_message`.

## Control Flow
The test creates a mock session, pushes a message manually, retrieves it, obtains the event handler, invokes error and message callbacks with new strings, checks the last message each time, and asserts unsupported callbacks are null.

## State And Persistence Behavior
State is the mock session's in-memory callback-message queue or last-message store. No persistence.

## Dependencies And Integration Points
Depends on Catch2, `wiredtiger.h`, and the `mock_session` wrapper. It supports tests that expect WiredTiger error/message callbacks to be capturable.

## Risks And Edge Cases
Ensures the mock handler exposes only implemented callbacks and records both error and message paths.

## Test Signals
Exact message strings must be returned after direct insertion and callback invocation; `handle_close`, `handle_general`, and `handle_progress` must be null.
