# sources/object-store/openstack-swift/swift/common/middleware/read_only.py

Purpose: Blocks write methods for an entire cluster or for individual accounts marked read-only through account sysmeta.

Important APIs and control flow: `ReadOnlyMiddleware.__init__` reads cluster `read_only`, builds the write-method set as `COPY`, `POST`, `PUT`, and optionally `DELETE`, and records a logger. `__call__` passes through non-write methods and non-Swift paths, parses the account from `/v1/...`, handles `COPY` with `Destination-Account` by validating the destination account, then calls `account_read_only`. If read-only applies, it returns `HTTPMethodNotAllowed`; otherwise it delegates. `account_read_only` calls `get_info(..., swift_source='RO')` and lets account sysmeta `read-only` override the cluster default when present.

State, dependencies, and integration: State is config-only. It depends on account info cache/proxy lookups, `check_account_format`, `valid_api_version`, and optional registration of `read_only` in `/info`.

Risks and test signals: COPY destination semantics are easy to miss because the write target may differ from the source account. Tests should cover cluster read-only true/false, account sysmeta true/false overrides, `allow_deletes`, invalid paths, invalid API versions, and Destination-Account validation.
