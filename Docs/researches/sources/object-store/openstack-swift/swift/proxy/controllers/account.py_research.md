# sources/object-store/openstack-swift/swift/proxy/controllers/account.py

## Purpose
This module implements the proxy controller for account-level requests. It validates account operations, fans requests out to account-server replicas, manages account info cache entries, handles account autocreate behavior, and controls which owner-only headers/ACLs are exposed.

## Important APIs, Types, and Functions
`AccountController` extends `Controller` with `server_type = 'Account'`. Its public request handlers are `GETorHEAD()`, `PUT()`, `POST()`, and `DELETE()`. `add_acls_from_sys_metadata()` converts internally stored account ACL sysmeta into external `x-account-access-control` when the requester is a Swift owner.

## Control Flow
Construction unquotes the account name and, if account management is disabled, removes `PUT` and `DELETE` from the controller's allowed methods. `GETorHEAD()` validates the account-name length, builds a `NodeIter`, forces JSON listing format, and delegates backend reads to `GETorHEAD_base()`. A backend 404 with deleted status becomes 410. If account autocreate is enabled, missing accounts can return a fake account listing marked by `X-Backend-Fake-Account-Listing`. The response is cached via `set_info_cache()`, owner ACLs are translated for owners, and owner-only headers are stripped for non-owners.

`PUT()` and `POST()` validate metadata and name length, generate backend headers, clear the account info cache, and call `make_requests()` against the account ring. `POST()` can autocreate a missing account and retry. `DELETE()` rejects any query string as a safety guard, checks management permission, clears cache, and fans out `DELETE`.

## State and Persistence Behavior
The controller does not persist directly; account servers persist account DB changes. Proxy-side state changes are cache invalidation (`clear_info_cache`) before mutating methods and cache population after account reads. It also mutates response headers to hide or expose owner-only metadata.

## Dependencies and Integration Points
It relies on the base controller fan-out/quorum machinery, account ring, listing format middleware, ACL parsing/formatting helpers, metadata validation, and Swift app flags including `allow_account_management`, `account_autocreate`, `swift_owner_headers`, and `recheck_account_existence`.

## Risks and Edge Cases
Fake account listings are intentionally not proof of actual account DB existence; downstream container PUT logic must respect `X-Backend-Fake-Account-Listing`. Owner-only header stripping is security-sensitive. Management-disabled deployments must not expose PUT/DELETE. Query-string rejection on DELETE protects middleware conventions. Account name length limits may be doubled for auto-create accounts through inherited base logic.

## Test Signals
Tests should cover GET/HEAD cache population, deleted account 410 mapping, fake autocreate listings, metadata validation failures, ACL sysmeta translation, owner header stripping, management-disabled method rejection, POST autocreate retry, DELETE query-string rejection, and quorum response selection from account replicas.
