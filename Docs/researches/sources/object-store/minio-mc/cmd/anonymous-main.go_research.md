# sources/object-store/minio-mc/cmd/anonymous-main.go

## Purpose

`anonymous-main.go` implements `mc anonymous`, managing anonymous bucket/prefix access policies and listing public links.

## Important APIs, Types, and Functions

`anonymousCmd` supports `set`, `set-json`, `get`, `get-json`, `list`, and `links` with `--recursive`. Message types are `anonymousRules`, `anonymousMessage`, and `anonymousLinksMessage`. Core helpers include `checkAnonymousSyntax`, `accessPermToString`, `stringToAccessPerm`, `doSetAccess`, `doSetAccessJSON`, `doGetAccess`, `doGetAccessRules`, `runAnonymousListCmd`, `runAnonymousLinksCmd`, and `runAnonymousCmd`.

## Control Flow

The main handler validates operation-specific arity and permission names, sets output color, and dispatches by operation. Set operations create a client and call `SetAccess`, optionally reading a JSON policy file capped at 120 KiB. Get operations call `GetAccess`. List retrieves access rules and prints resource-policy mappings. Links retrieves rules, filters readable rules under the requested path, lists matching objects, encodes public URLs, and prints them.

## State and Persistence Behavior

Anonymous policy state is persisted remotely by the S3-compatible server. Locally, the command reads optional JSON files and writes output only.

## Dependencies and Integration Points

It depends on generic `newClient`, client `SetAccess`, `GetAccess`, `GetAccessRules`, `List`, URL/alias helpers, `accessPerms` definitions from elsewhere, probe errors, and global context.

## Risks and Edge Cases

`set-json` uses `io.ReadFull` with a fixed buffer and treats a file larger than 120 KiB as too large. `links` filters rules by string prefix and only includes download/public permissions. Error handling maps `APINotImplemented` to clearer messages for non-S3 targets. Custom anonymous JSON is passed through server-side validation.

## Test Signals

Tests should cover operation arity, permission mapping, custom JSON size limit, non-S3 API errors, list/links filtering, recursive behavior, and get-json unmarshalling.
