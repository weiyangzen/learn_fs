# sources/storage-engines/pebble/internal/lsmview/url.go

## Purpose
This file converts an `lsmview.Data` value into a shareable visualization URL. The payload is JSON-encoded, zlib-compressed, base64 URL-encoded, and stored in the URL fragment.

## Important APIs, Types, And Functions
`GenerateURL(data Data) (url.URL, error)` is the only exported function. It JSON-encodes the data into a buffer, compresses the JSON through a zlib writer, base64 URL-encodes the compressed bytes, closes both encoders, and returns an HTTPS URL targeting `raduberinde.github.io/lsmview/decode.html` with the encoded payload as `Fragment`.

## Control Flow
The function is linear: JSON encode, create nested encoders, stream the JSON buffer into zlib, close the zlib writer to flush the compressed stream, close the base64 encoder to flush padding/final bytes, and construct the URL. Each serialization step returns early on error. The function does not attempt to decode or validate the data after encoding.

## State, Persistence, And Side Effects
There is no durable local state. The encoded state is persisted in the URL fragment. The fragment is not sent to the server in normal HTTP requests, which keeps the full LSM payload client-side for the static viewer. The function allocates intermediate buffers proportional to the JSON and compressed payload sizes.

## Dependencies And Integration Points
The function depends on `bytes`, `compress/zlib`, `encoding/base64`, `encoding/json`, and `net/url`. Its integration boundary is the external viewer's expected fragment encoding; the test fixture locks down this encoding including the host, path, zlib stream, and base64 alphabet.

## Risks And Edge Cases
Large LSMs may produce URLs that exceed browser or sharing limits because all data lives in the fragment. `base64.URLEncoding` includes padding, so changing to raw encoding would break compatibility. The function uses `json.Encoder.Encode`, which appends a newline before compression; the test captures that exact behavior. Any change in compression level or JSON encoding can invalidate stable test vectors.

## Test Signals
`url_test.go` builds a two-level, four-table dataset and asserts the exact URL string. This gives strong regression coverage for the encoding pipeline and the viewer endpoint, but it does not test decoding, invalid data, or very large payload behavior.
