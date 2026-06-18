# Research: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_single_thread_check.cpp

## sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_single_thread_check.cpp

Purpose: Diagnostic-only Catch2 test for `__wt_single_thread_check_start` assertion reporting when optional session fields are null.

Important conditions/APIs: compiled only when both `HAVE_DIAGNOSTIC` and `HAVE_UNITTEST_ASSERTS` are defined. Uses `mock_session`, `WT_SESSION_IMPL`, `session->thread_check.lock`, `__wt_spin_lock`, `__wt_spin_unlock`, `__wt_thread_id`, and unittest assertion capture fields `unittest_assert_hit` and `unittest_assert_msg`.

Control flow: the test sets `session->id`, manually takes the thread-check spin lock to force `__wt_spin_trylock` inside the check to return `EBUSY`, calls `__wt_single_thread_check_start`, then compares the captured assertion text to an exact string. The crafted expected string proves null name, last op, dhandle, and owning thread fields are rendered as `none`/`0` instead of crashing.

State and persistence: no persistent state. It mutates diagnostic lock state and assertion capture fields, then releases the lock.

Dependencies/integration: integrated with WiredTiger diagnostic assertion plumbing and thread-id formatting. Risks are exact-message brittleness across wording changes and platform thread id formatting. Test signals are assertion-hit flag and exact assertion message.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_single_thread_check.cpp -->
