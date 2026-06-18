# sources/user-network-fs/samba/source4/dsdb/tests/python/notification.py

## Purpose

`notification.py` tests Samba LDAP notification search behavior. It verifies that notification searches deliver modified objects, enforce the maximum number of outstanding notification searches, and reject unsupported notification filters and attributes.

## Important APIs, Types, and Functions

- `LDAPNotificationTest.setUp()` opens a `SamDB`, discovers the domain DN, reads rootDSE `tokenGroups`, unpacks a SID, and builds a `<SID=...>` DN for the current user.
- `test_simple_search()` compares normal search results with notification results after modifying `otherLoginWorkstations`.
- `test_max_search()` opens six notification iterators and expects five timeouts plus one admin-limit failure.
- `test_invalid_filter()` enumerates valid notification filter attributes and many invalid filter shapes, then checks every schema attribute other than the allowlist is rejected.
- The tests use `SamDB.search_iterator()` with `controls=["notification:1"]` and `timeout` values to observe asynchronous search behavior through Python iteration and `result()`.

## Control Flow

Setup resolves the current authenticated user by token-group SID. `test_simple_search()` first captures that user's baseline message via a SID DN search, then finds the same object under the domain subtree. It modifies `otherLoginWorkstations` to `BEFORE`, starts a notification subtree search with a one-second timeout, modifies the attribute to `AFTER`, iterates notification replies until the target object is observed, and expects `notify1.result()` to end with `ERR_TIME_LIMIT_EXCEEDED`.

`test_max_search()` starts `max_notifications + 1` notification searches. Iterating each handle should either time out or fail with `ERR_ADMIN_LIMIT_EXCEEDED`; exactly one admin-limit failure and five time-limit failures are expected.

`test_invalid_filter()` proves simple presence filters and OR filters over `objectClass`, `objectGUID`, `distinguishedName`, and `name` can be accepted until timeout. It then verifies AND, equality, range, substring, and NOT filters are rejected with `ERR_UNWILLING_TO_PERFORM`. Finally it walks schema `attributeSchema` objects with paged results and checks notification presence filters on non-allowlisted attributes are rejected, including a nonexistent attribute name.

## State and Persistence Behavior

The module mutates only the current user's `otherLoginWorkstations` attribute and deletes that attribute after the simple notification test. Notification search handles are transient server-side operations that consume per-connection or server notification slots until they time out or return an admin-limit error. The tests run only for LDAP URLs; TDB/local URLs are explicitly failed.

## Dependencies and Integration Points

The file depends on `SamDB`, `search_iterator`, LDAP notification controls, LDB error codes, rootDSE token group generation, NDR SID unpacking, schema searches, and paged-results controls. It directly exercises DSDB notification indexing/filter validation and server resource-limit enforcement.

## Risks and Edge Cases

- Notification tests are timing-sensitive because success is expressed as timeout after expected notifications are delivered.
- The max-notification count is hardcoded to five; configuration changes to notification limits require updating the test.
- The simple test modifies a real account attribute on the authenticated user and must clean it up even after failures.
- Valid filter semantics are deliberately narrow; broadening notification support requires revisiting many `ERR_UNWILLING_TO_PERFORM` expectations.

## Test Signals

Signals include receiving exactly one changed target object during notification search, timeout rather than success on accepted notification filters, one admin-limit rejection among six concurrent searches, rejection of unsupported filters and attributes, and correct cleanup of `otherLoginWorkstations`.
