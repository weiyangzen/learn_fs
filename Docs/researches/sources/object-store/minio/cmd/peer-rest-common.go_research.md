# sources/object-store/minio/cmd/peer-rest-common.go

## Purpose
This file centralizes peer REST versioning, route paths, query/form key names, and a restart/update delay constant shared by peer client and server code.

## Important APIs, Types, and Functions
`peerRESTVersion` is `v39`, with `peerRESTPath` rooted under the MinIO reserved peer path. Constants define legacy method routes such as `/health`, `/verifybinary`, `/speedtest`, `/devnull`, and `/getreplicationmrf`. Key constants cover bucket/user/policy/signal/profiler/perf/metrics/listen parameters. `restartUpdateDelay` is 250 ms.

## Control Flow and State
There is no runtime control flow or state. This file is a compatibility contract.

## Dependencies and Integration Points
Both `peer-rest-client.go` and `peer-rest-server.go` consume these constants. Route versioning must remain aligned with registered handlers and remote clients during rolling updates.

## Risks and Test Signals
Changing route names or version without coordinated compatibility breaks internode communication. Query key mistakes can silently route wrong parameters to admin operations. Compilation catches missing constants, but behavioral compatibility relies on integration tests and rolling-upgrade discipline.
