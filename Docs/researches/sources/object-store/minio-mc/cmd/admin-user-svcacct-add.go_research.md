# sources/object-store/minio-mc/cmd/admin-user-svcacct-add.go

## Purpose

`admin-user-svcacct-add.go` implements `mc admin user svcacct add` and defines shared service-account output, credential generation, operation constants, and time parsing used by multiple service-account commands.

## Important APIs, Types, and Functions

`adminUserSvcAcctAddFlags` includes access key, secret key, policy, name, description/comment, and expiry. `acctMessage` formats service and STS account records. `acctOp` constants drive output behavior. `supportedTimeFormats` defines accepted expiry formats. `generateCredentials` creates random access and secret keys. `mainAdminUserSvcAcctAdd` calls `AddServiceAccount`.

## Control Flow

The handler validates target and parent account, reads flags, maps deprecated `--comment` into description, generates missing credentials, creates an admin client, validates optional policy JSON with `policy.ParseConfig` and rejects empty policies, parses optional expiry in local time using known formats, calls `client.AddServiceAccount`, and prints generated credentials and expiration.

## State and Persistence Behavior

The server persists the new service account and optional embedded policy/expiration. Local state is limited to random credential material and output. JSON output can include generated secret keys.

## Dependencies and Integration Points

It depends on crypto randomness, base64, MinIO policy parsing, `madmin.AddServiceAccountReq`, shared console output, and sibling service-account commands that reuse `acctMessage`, constants, and `supportedTimeFormats`.

## Risks and Edge Cases

Generated secrets replace `/` with `+` after base64 truncation. Expiry parsing uses the local timezone, which can produce environment-dependent results. Empty policy documents are rejected client-side. Secrets are printed on success and must be handled carefully by callers.

## Test Signals

Tests should cover random credential length/charset, partial credential generation, policy parse and empty-policy rejection, expiry formats and invalid expiry, deprecated comment handling, and output redaction expectations.
