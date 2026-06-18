## sources/user-network-fs/gcsfuse/internal/gcsx/compose_object_creator.go

Purpose: implements an append-style `objectCreator` that writes appended bytes to a temporary object and composes the existing source object plus temporary object back over the source object.

Important APIs/types/functions: `newComposeObjectCreator(prefix, bucket)`, `composeObjectCreator`, `chooseName`, and `Create`. `chooseName` reads 64 random bits from `crypto/rand` and formats a temporary object name with the configured prefix. `Create` accepts the existing `srcObject`, optional mtime, upload retry/timeout values, and an `io.Reader` containing appended content.

Control flow: `Create` chooses a temporary name, creates a temp object with `bucket.CreateObject`, defers best-effort deletion of that temp object, copies source metadata, optionally writes `gcs.MtimeMetadataKey`, then calls `bucket.ComposeObjects` with two sources: original object generation and temp object generation. Destination generation and metageneration preconditions preserve source-object consistency.

State and persistence: no local persistent state beyond prefix and bucket. Remote persistent effects are temp object creation, destination compose overwrite, and temp deletion. Temp deletion uses generation `0` to remove the latest temp generation; failures are returned only when compose succeeded.

Dependencies/integration: uses GCS object metadata and precondition semantics, `maps.Copy`, `time.RFC3339Nano`, and wraps `gcs.NotFoundError` from compose as `gcs.PreconditionError` because source clobber is the likely cause.

Risks/test signals: temp cleanup can fail and requires external garbage collection. Source metadata is copied shallowly. NotFound conversion may mask rare temp-object deletion races as source precondition failures. Tests cover temp naming, compose request shape, property preservation, error wrapping, precondition conversion, and cleanup.
