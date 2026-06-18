# sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/FollowerAppendLogEntryGenerator.java

## Purpose
Freon/Vapor generator that acts as a fake Ratis leader and streams append entries directly to an isolated follower datanode.

## Important APIs, types, and functions
Command `falg`, options for pipeline id, chunk size, batching, next index, and rate limit. Extends `BaseAppendLogGenerator` and implements gRPC `StreamObserver<AppendEntriesReplyProto>`. Uses Ratis gRPC stubs, group management, vote requests, append entries, Ozone `ContainerCommandRequestProto` write-chunk payloads, in-flight queue, and metrics timer.

## Control flow
`call` initializes payload, server id, fake leader peer, plaintext gRPC channel, optional rate limiter, Freon state, and append stream. If starting from index zero, it configures a two-peer group, requests a vote, sends an initial configuration log entry, then runs Freon operations that generate batched write-chunk log entries. Replies remove call IDs and warn when follower commit lags.

## State and persistence behavior
Mutates the target follower’s Ratis log and datanode chunk/container state through append entries. Maintains client-side `nextIndex`, in-flight call IDs, and optional rate limiter.

## Dependencies and integration points
Integrates Ratis server protocol gRPC, Ratis client group management, Ozone container protobuf commands, Freon metrics, and local datanode identity discovery.

## Risks and edge cases
Requires exactly one Freon thread. Uses plaintext and fake fixed IDs/addresses. Initial config peer id uses `serverAddress` in one place, which may not match UUID server id. Data is generated for testing, not secure randomness.

## Test signals
No direct tests. Signals are vote success, append replies, in-flight queue draining, commit lag warnings, and `append-entry` timing.
