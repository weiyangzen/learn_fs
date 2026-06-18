# sources/object-store/minio-mc/cmd/admin-policy-create.go

## Purpose
Implements `mc admin policy create`, uploading a canned IAM policy JSON document to a MinIO server.

## Important APIs, types, and functions
`adminPolicyCreateCmd` declares the command. `checkAdminPolicyCreateSyntax` requires target, policy name, and policy file. `userPolicyMessage` formats create/list/info/remove/legacy attach/detach messages. `mainAdminPolicyCreate` reads the policy file and calls `AddCannedPolicy`.

## Control flow
The handler validates arity, sets output color, reads the policy JSON from disk using `os.ReadFile`, opens an admin client, sends the bytes to `AddCannedPolicy`, and prints a success message naming the policy.

## State and persistence behavior
Remote IAM policy state is created or replaced according to server semantics. The command reads a local policy file but does not persist local output.

## Dependencies and integration points
It integrates local filesystem input, MinIO admin canned-policy APIs, `probe` tracing over CLI args, global context, console colors, and shared policy message serialization.

## Risks and edge cases
Policy JSON validation is delegated to the server; local code only reads bytes. Large or unreadable files fail before the admin call. `userPolicyMessage` is shared, so changes can affect unrelated policy subcommands.

## Test signals
Tests should cover arity validation, unreadable file errors, successful byte payload to `AddCannedPolicy`, JSON and human output, and invalid policy document server errors.
