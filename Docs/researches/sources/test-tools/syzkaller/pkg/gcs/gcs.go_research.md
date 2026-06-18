# sources/test-tools/syzkaller/pkg/gcs/gcs.go

## Purpose
`gcs.go` wraps Google Cloud Storage for syzkaller code that needs to upload, read, publish, delete, test, and list bucket objects. It hides the `cloud.google.com/go/storage` client behind a small `Client` interface and assumes Application Default Credentials when constructing a real client.

## Important APIs, Types, And Functions
`Client` defines the storage surface: `Close`, `FileReader`, `FileWriter`, `DeleteFile`, `FileExists`, `ListObjects`, and `Publish`. `UploadOptions` controls optional public ACL publishing, content encoding, and test injection via `GCSClientMock`. `UploadFile` is the high-level upload helper. `NewClient` returns the concrete `client` wrapper. `Object` is the minimal listing record with path and creation time. `GetDownloadURL` maps bucket/object paths to either public or authenticated Cloud Storage URLs. `ErrFileNotFound` normalizes delete misses. The private `split` helper parses `bucket/object` paths.

## Control Flow
`UploadFile` strips a leading `gs://`, creates or uses an injected client, defers `Close`, obtains a writer, streams all input via `io.Copy`, closes the writer, and optionally calls `Publish`. Read operations call `split`, fetch object attributes, reject deleted objects, then create a conditional reader pinned to the observed generation and metageneration. Writes create a GCS object writer and set content type or encoding only when provided. Listing parses bucket plus optional prefix, iterates `Objects`, converts iterator completion to a normal break, and wraps query errors.

## State And Persistence Behavior
The concrete client holds a `storage.Client` and context; persistent state lives remotely in GCS buckets and object metadata. `FileReader` uses generation preconditions to avoid racing a changing object after attributes are read. `FileWriter` persists data only once the returned writer is closed successfully. `Publish` mutates the object ACL by granting `AllUsers` reader access. `DeleteFile` maps `storage.ErrObjectNotExist` to package-local `ErrFileNotFound`.

## Dependencies And Integration Points
This package depends on `cloud.google.com/go/storage`, `google.golang.org/api/iterator`, `context`, and Go I/O primitives. Callers can mock through the `Client` interface; the generated mock in `pkg/gcs/mocks` is built against this contract. Public URL construction assumes the Cloud Storage HTTP hostnames used by syzkaller dashboards or reports.

## Risks And Edge Cases
`split` rejects paths without a slash; `ListObjects` treats that error as a bucket-only listing, but other methods return it. `UploadFile` ignores `Close` errors from the client itself because it is deferred without checking. If `io.Copy` fails, it attempts to close the writer but returns only the copy error. Publishing after upload is a second operation, so upload success with ACL failure is possible. `GetDownloadURL` only trims leading slash, not `gs://`, so callers must pass normalized `bucket/object` strings.

## Test Signals
Useful coverage would verify mocked `UploadFile` call ordering, `gs://` trimming, writer close failure propagation, publish-on-demand behavior, delete miss normalization, bucket-only `ListObjects`, and URL prefix selection. The presence of a generated testify mock indicates downstream tests are expected to isolate this package from live GCS.
