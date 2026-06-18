# sources/user-network-fs/gcsfuse/internal/storage/object_writer.go

## Purpose
This file adapts the Google Cloud Storage `*storage.Writer` to the local `gcs.Writer` interface.

## Important APIs and Control Flow
`ObjectWriter` embeds `*storage.Writer`. `ObjectName` returns `Writer.Name`, and `Attrs` delegates to `Writer.Attrs()`. `Flush`, `Write`, and `Close` are provided by the embedded storage writer, satisfying the rest of `gcs.Writer`.

## State, Dependencies, and Integration
State is the embedded storage writer and its upload session. The file depends on `cloud.google.com/go/storage`. It integrates with bucket upload flows that need to return a local interface rather than the concrete Google client writer.

## Risks and Test Signals
The file comments note unit tests are absent because fake-storage-server does not support multiple versions of the same object even though versioning APIs exist. Behavior therefore depends on integration tests around chunked/resumable uploads. A nil embedded writer would panic on `ObjectName` or `Attrs`.
