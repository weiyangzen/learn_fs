# sources/object-store/minio/cmd/metacache-marker.go

## Purpose

`metacache-marker.go` embeds and extracts metacache continuation metadata in S3 listing markers. It lets clients resume cached listings by carrying cache ID, pool, and set information inside an otherwise normal marker string.

## Important APIs, Control Flow, And State

`markerTagVersion` is `"v2"`. `(*listPathOptions).parseMarker` only acts on markers containing `[minio_cache:v2`. It splits the marker at the last `[`, keeps the user-visible marker prefix, then parses comma-separated `key:value` tags from the final bracketed section. `id` restores the cache ID; `return` creates a fresh ID and sets `Create` to true; `p` and `s` parse pool and set indexes. Parse failures for pool/set reset to a fresh ID with `Create` true, forcing a new listing path. Unknown tags are ignored.

`(listPathOptions).encodeMarker` appends either `[minio_cache:v2,return:]` when no ID exists or `[minio_cache:v2,id:<id>,p:<pool>,s:<set>]` when resuming a concrete cache. It logs internally if the ID contains characters that break the simple parser (`[`, `:`, or `,`).

The file has no persistent state; it mutates `listPathOptions` fields and relies on callers in `metacache-server-pool.go`.

## Risks And Test Signals

Risks include ad hoc parsing with `strings.Split(tag, ":")`, collision with object names containing bracketed text, malformed trailing brackets, and marker IDs containing reserved characters. There are no direct tests in this subset, so marker compatibility is mostly protected by listing integration tests.
