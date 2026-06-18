# sources/user-network-fs/rclone/lib/rest/rest.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/rest/rest.go -->
## sources/user-network-fs/rclone/lib/rest/rest.go

Purpose: implements rclone's reusable REST client wrapper around `http.Client`, adding root URLs, default/extra headers, signing, redirects, multipart uploads, JSON/XML helpers, and response/error handling.

Important APIs and control flow: `NewClient` initializes `Client` with a default error handler. Setter methods update root URL, headers, signer, basic auth, and cookies under a mutex. `Call(ctx, opts)` validates options/root URL, builds the URL and request, wraps bodies with `readers.NoCloser`, handles content length/range/type, transfer encoding, trailers, open options, basic auth, redirect policy, signer invocation, HTTP execution, non-2xx error handling, and no-response draining. `CallJSON`/`CallXML` use `callCodec`, which marshals request bodies, optionally builds multipart bodies with `MultipartUpload`, calls `Call`, and decodes responses. `DecodeJSON`/`DecodeXML` drain and close bodies. Redirect helpers build client copies with specific `CheckRedirect` policies.

State, dependencies, and integration: `Client` stores `*http.Client`, root URL, default headers, error handler, and signer protected by `sync.RWMutex`. It depends on encoding packages, `multipart`, `http`, rclone `fs`, and `readers`. Integration is broad across rclone backends as the common HTTP API shim.

Risks and test signals: `Call` manually unlocks/relocks around signer and `Do`, which avoids blocking setters but is delicate; copied header maps prevent mutation races. `MultipartUpload` starts goroutines and relies on context cancellation/reader closure. `opts.ContentLength` may be mutated when multipart overhead is added. Tests in this subset cover only URL and header helpers, not `Call`, redirects, multipart, signer, or error handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/rest/rest.go -->
