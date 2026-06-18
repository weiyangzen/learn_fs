# sources/object-store/minio-mc/cmd/admin-policy-entities.go

## Purpose
Implements `mc admin policy entities`, listing policy associations for selected users, groups, policies, or all entities.

## Important APIs, types, and functions
`adminPolicyEntitiesFlags` provides string-slice `--user`, `--group`, and `--policy`. `mainAdminPolicyEntities` builds `madmin.PolicyEntitiesQuery` and calls `GetPolicyEntities`, then prints `policyEntitiesFrom(res)`.

## Control flow
The handler requires exactly one target alias. It reads repeated query flags, creates an admin client, requests association entities from the server, and delegates output shaping to the existing policy-entities renderer.

## State and persistence behavior
This is read-only. It observes IAM association metadata and does not modify policies, users, or groups.

## Dependencies and integration points
It integrates the MinIO admin policy-entities API, CLI string-slice flags, global context, `probe` errors, and renderer helpers defined elsewhere in the command package.

## Risks and edge cases
The command allows all three query dimensions together, relying on server semantics for intersection/union behavior. Empty flag lists mean all relevant associations. Output details depend on `policyEntitiesFrom`, not this file.

## Test signals
Tests should cover one-target syntax, repeated flags, empty query lists, server errors, and output conversion for user, group, and policy association results.
