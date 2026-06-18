# sources/storage-engines/foundationdb/fdbkubernetesmonitor/api/annotations.go

## Purpose
This Go file centralizes Kubernetes annotation keys used by the FoundationDB Kubernetes monitor and launcher ecosystem.

## Important APIs, Types, And Functions
Constants include `CurrentConfigurationAnnotation`, `EnvironmentAnnotation`, `OutdatedConfigMapAnnotation`, `DelayShutdownAnnotation`, `ClusterFileChangeDetectedAnnotation`, and `IsolateProcessGroupAnnotation`.

## Control Flow
There is no executable control flow. Other packages import these constants to read/write annotations consistently.

## State And Persistence Behavior
The constants name persistent Kubernetes Pod or ConfigMap annotations. The file itself does not access the Kubernetes API.

## Dependencies And Integration Points
It integrates with monitor logic that stores current launcher configuration/environment, detects outdated config maps, delays shutdown, flags cluster-file changes, and isolates process groups for debugging.

## Risks And Edge Cases
Annotation key drift breaks interoperability with the operator/launcher. Values such as durations or booleans must be validated by consuming code, not here.

## Test Signals
Tests should assert exact annotation string values where other components rely on them, especially upgrade/backward-compatibility tests.
