# sources/test-tools/syzkaller/pkg/gce/gce.go

## Purpose
Package `gce` wraps Google Compute Engine APIs for syzkaller managers running on GCE. It discovers the current project, zone, network, and instance metadata, creates/deletes worker instances and images, rate-limits API calls, and tracks preferred zones for preemptible capacity.

## Important APIs, Types, And Functions
`Context` stores project/zone/region, current instance and IPs, network/subnetwork, preemptible and normal zone lists, compute service, metadata server, and API rate gate. `zoneList` stores preferred zone, ordered zone list, and scores. `InstanceConfig` describes worker VM creation parameters; `CreateArgs` exists for simple creation options.

`NewContext` creates an OAuth-backed compute service, reads metadata, validates zone, derives region, discovers current instance network/IPs, queries regional zones, and initializes zone lists. `CreateInstance` builds a `compute.Instance`, handles C4A disk sizing, nested virtualization, display device, spot/preemptible scheduling, max runtime deletion, zone retry/fallback, waits for operation completion, then returns internal IP and zone. `DeleteInstance`, `DeleteInstanceAcrossZones`, `IsInstanceRunning`, `CreateImage`, and `DeleteImage` wrap corresponding Compute APIs. `waitForCompletion` polls global/zonal operations and maps resource-pool exhaustion to `resourcePoolExhaustedError`. `apiCall` rate-gates and backs off rate-limit errors. Helpers include `localZone`, `validateZone`, `zoneToRegion`, `promote`, zone score updates, `ReportPreemption`, and `zoneList.get`.

## Control Flow
Initialization performs metadata reads before Compute API reads so it can address the current instance. Instance creation iterates scored zones; on resource exhaustion it tries later zones, and for preemptible instances can fall back to standard provisioning after exhausting preemptible zones. Operation waits loop until `DONE` or error. Zone scoring decays each insertion attempt and rewards success, then stable-sorts by score with preferred-zone promotion as a tie breaker.

## State And Persistence Behavior
GCE resources are persistent cloud state: instances, disks, images, metadata, scheduling policy, and network attachments. Local `Context` state caches zone scores and network metadata for the process. API rate gating is process-local. Delete helpers intentionally treat 404 as success for idempotence.

## Dependencies And Integration Points
The package depends on Google OAuth, Compute API client, Google API errors, metadata via HTTP, syzkaller logging, and target OS constants. It integrates with VM manager code that provisions fuzzing workers and images in the current GCE project/region.

## Risks
The package assumes it runs on GCE and can query metadata. `getMeta` does not check HTTP status codes before returning body text. `apiCall` uses a one-second ticker, making operations conservative but potentially slow. Zone scoring is in-memory and randomizes preferred zone 5 percent of the time, so behavior can vary across runs. `CreateInstance` returns immediately on an insert API error rather than trying later zones; only operation-level resource exhaustion uses zone fallback.

## Test Signals
`gce_test.go` covers zone validation, region extraction, C4A disk sizing, metadata local-zone parsing, and zone prioritization/score changes. Cloud API operations are not directly tested here.
