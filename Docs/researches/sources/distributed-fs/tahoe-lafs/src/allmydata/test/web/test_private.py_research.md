# sources/distributed-fs/tahoe-lafs/src/allmydata/test/web/test_private.py

## Purpose
This module tests authentication behavior for Tahoe private web resources created by `create_private_tree`. It ensures requests without the expected scheme/token are rejected and correctly authorized requests pass through to the underlying tree.

## Important APIs, Types, And Functions
`PrivacyTests` builds a private resource tree using a token callback, wraps it in `RequestTraversalAgent`, and uses treq `HTTPClient`. `_authorization` builds Twisted `Headers`. Tests reference `SCHEME`, `UNAUTHORIZED`, `NOT_FOUND`, and `has_response_code`.

## Control Flow
The tests issue HEAD requests to a made-up path. Missing authorization, wrong scheme, and wrong token must all return `401 Unauthorized`. A request with the configured Tahoe scheme and token should not be rejected by authentication; because the path is made up, it reaches normal routing and returns `404 Not Found`.

## State And Persistence
The only state is the in-memory token and resource tree. No persistent state or external network is used.

## Dependencies And Integration Points
It integrates `allmydata.web.private`, Twisted HTTP headers/status codes, treq in-process traversal, testtools Twisted matchers, and the local response-code matcher.

## Risks And Test Signals
The tests strongly signal scheme/token enforcement and pass-through after successful authentication. Risks include lack of coverage for timing-safe comparison, malformed authorization headers, methods beyond HEAD, and actual private child resources.
