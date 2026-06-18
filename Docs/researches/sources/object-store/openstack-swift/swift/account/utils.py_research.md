# sources/object-store/openstack-swift/swift/account/utils.py

Purpose: shared helpers for account responses and account listing serialization. It centralizes account stat headers and the account listing body used by the account server and tests.

Important APIs: `FakeAccountBroker` is a minimal broker-like object for empty account responses. `get_response_headers(broker)` converts broker info, policy stats, and account metadata into HTTP headers. `account_listing_response()` obtains container rows from `broker.list_containers_iter()` and formats XML, JSON, plain-text, or empty `204` responses.

Control flow: `account_listing_response()` defaults to `FakeAccountBroker`, builds headers first, then transforms broker rows into dictionaries. Subdir rows become `{'subdir': name}`; container rows include name, count, bytes, last_modified, and storage policy name when the policy index exists. Content type suffix selects XML, JSON, text, or no-content response.

State and persistence: no direct persistence; all state comes from the broker. Response headers expose account counts, bytes, creation and PUT timestamps, storage-policy stats, and non-empty broker metadata.

Dependencies and integration: uses `Timestamp`, `POLICIES`, account listing limits, listing format utilities, and swob responses. `server.py` uses both exported helpers for `GET` and `HEAD`.

Risks: metadata with empty values is suppressed, unknown policy indexes intentionally omit storage-policy names, and JSON output is ASCII encoded. Tests should cover policy stats, reserved-name allowance forwarding, delimiter/subdir listings, empty account responses, and every response format.
