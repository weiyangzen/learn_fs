# sources/user-network-fs/rclone/backend/imagekit/client/url.go

## Purpose
Generates public or signed ImageKit delivery URLs from existing file URLs and optional query parameters.

## Important APIs, Types, and Functions
`URLParam` contains path/source URL, endpoint override, signed flag, expiry seconds, and query parameters. `ImageKit.URL` returns a URL string and optional HMAC-SHA1 signature parameters.

## Control Flow
The function chooses an endpoint, normalizes a trailing slash, parses `Src`, merges caller query parameters, and serializes the URL. If signing is requested, it calculates expiry as `now + ExpireSeconds`, strips the endpoint prefix from the result URL to build the signing path, appends expiry to that path, computes HMAC-SHA1 using `PrivateKey`, and appends `ik-t` and `ik-s` query parameters.

## State and Persistence
No state is persisted. The only time-varying state is the current Unix timestamp used for signed URLs.

## Dependencies and Integration Points
Used by backend `PublicLink` and `Object.Open`. Depends on standard `crypto/hmac`, `sha1`, URL parsing, and the ImageKit private key.

## Risks and Edge Cases
`URLParam.Path` is unused. If `Src` does not start with the selected endpoint, signing will use the full URL as the path input after a no-op replace, which may produce invalid signatures. Negative or zero expiry values are not rejected. Signing includes query parameters already inserted into `resultURL`, so changes to query encoding affect signatures.

## Test Signals
There are no local tests for signature construction or endpoint edge cases.
