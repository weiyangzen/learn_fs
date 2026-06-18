# sources/object-store/minio/cmd/site-replication_test.go

## Purpose

`site-replication_test.go` provides a focused unit test for one helper in the site replication subsystem: `getMissingSiteNames`. That helper is used by `AddPeerClusters` to produce a user-facing list of already-replicated sites omitted when extending an existing site replication setup.

## Important APIs, types, and functions

- `TestGetMissingSiteNames` is the only test function.
- The table uses `madmin.PeerInfo` values to model current replicated sites and `set.StringSet` values to model old and new deployment ID sets.
- The function under test, `getMissingSiteNames(oldDeps, newDeps, currSites)`, computes `oldDeps.Difference(newDeps)` and maps missing deployment IDs back to peer names from `currSites`.

## Control flow

The test defines three cases: an existing three-site setup where a new request includes only one deployment and should report the two omitted site names; a request that adds an unrelated new deployment while preserving all existing deployments and should report no missing names; and a non-replicated current setup with no current sites and should also report no names. Each case calls `getMissingSiteNames` and compares only the returned length with the expected length.

## State and persistence behavior

The test is pure and has no persistence, network, or global MinIO state. It constructs all peer and set data in memory. It does not verify ordering, string content, or mutation of input sets.

## Dependencies and integration points

The test imports Go's `testing` package, `madmin-go/v3` for `PeerInfo`, and `minio-go/v7/pkg/set` for deployment ID sets. Its production integration point is the validation branch in `SiteReplicationSys.AddPeerClusters` that rejects add requests missing currently replicated sites.

## Risks and edge cases

- The assertion checks only length, so a regression returning the wrong site names in the right count would pass.
- It does not check stable ordering of returned names, though the production helper follows `currSites` order.
- It does not test unknown deployment IDs in `oldDeps`, duplicate `currSites` names, nil sets, or nil current-site slices.
- It does not cover the wrapping error message in `AddPeerClusters`, so formatting regressions can slip through.

## Test signals

The test signals that `getMissingSiteNames` is expected to report only deployments that were in the old replicated set but absent from the new requested set, and to ignore new deployments that were not part of the prior replicated configuration. Coverage is narrow and helper-level only.
