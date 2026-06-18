## sources/user-network-fs/gcsfuse/internal/gcsx/content_type_bucket.go

Purpose: wraps a `gcs.Bucket` so object creation APIs infer a MIME content type from object name extension when the caller did not provide one.

Important APIs/types/functions: `NewContentTypeBucket`, `contentTypeBucket`, and overrides for `CreateObject`, `ComposeObjects`, `CreateObjectChunkWriter`, and `CreateAppendableObjectWriter`.

Control flow: each overridden method checks the incoming request’s `ContentType`. If empty, it calls `mime.TypeByExtension(path.Ext(name))` using `req.Name` or `req.DstName`, mutates the request in place, and forwards it to the embedded bucket.

State and persistence behavior: no stored state beyond the wrapped bucket. It mutates request objects before they hit storage, so downstream calls persist inferred content type metadata on new/composed objects. Explicit content types are preserved.

Dependencies/integration: standard `mime` and `path` packages; `gcs.Bucket` creation and writer interfaces. It composes cleanly with other bucket wrappers because it embeds and delegates to the underlying bucket.

Risks/test signals: request mutation may surprise callers reusing request values. Unknown extensions produce an empty content type, which is passed through. Tests cover create, compose, chunk writer, appendable writer, explicit override preservation, and extension inference.
