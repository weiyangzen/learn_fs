# sources/test-tools/syzkaller/syz-cluster/overlays/common/network-policy-reporter.yaml

## Purpose
Allows email reporter pods to access reporter-server pods.

## Important APIs, types, and functions
Defines `NetworkPolicy` `reporter-server-access` selecting `app: reporter-server`, with ingress allowed from `app: email-reporter`.

## Control flow
Under ingress deny, email reporter can call reporter-server APIs such as get-next-report, confirm, upstream, invalidate, and record-reply.

## State and persistence behavior
No persistence; controls network reachability to the report lifecycle service.

## Dependencies and integration points
Matches `Handler` use of `api.ReporterClient` and default reporter client wiring.

## Risks and edge cases
Only email reporter is allowed here; other intended reporter clients need their own policy. Ports are unrestricted for the allowed source.

## Test signals
Go tests use in-process test servers and do not validate this policy. Deployment/runtime integration validates it.
