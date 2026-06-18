# sources/test-tools/syzkaller/pkg/gerrit/gerrit.go

## Purpose
`gerrit.go` provides a small authenticated client for creating Linux Gerrit code-review changes, specifically against `https://linux-review.googlesource.com`.

## Important APIs, Types, And Functions
`CreateChange(ctx, repo, branch, baseCommit, description, diff)` maps a repository URL to a Gerrit project, builds a change creation request, posts it, and returns the Gerrit change number plus browser link. The private `request` helper performs authenticated JSON POSTs to Gerrit REST endpoints and decodes JSON responses after stripping Gerrit's XSSI prefix. `host` is the fixed Gerrit base URL.

## Control Flow
`CreateChange` calls `projectForRepo`, builds a request map with project, branch, subject, base commit, and inline patch content, then asks `request` to post to `changes/`. It constructs the returned link from the fixed host, project, and response `_number` regardless of whether `request` returns an error. `request` obtains a Google default token source with the Gerrit code review scope, JSON-marshals the request map, creates a context-bound `POST` to `/a/<api>`, executes it through an OAuth2 HTTP client, reads the response body, checks status, trims the `)]}'\n` XSSI prefix, and unmarshals into the caller-supplied response.

## State And Persistence Behavior
There is no local persistence. Remote state is created in Gerrit when the POST succeeds. Authentication state comes from Application Default Credentials and OAuth2 token handling. The request body is fully buffered in memory.

## Dependencies And Integration Points
The file depends on `golang.org/x/oauth2`, `golang.org/x/oauth2/google`, `net/http`, and JSON encoding. It integrates with `repos.go` for supported repository mapping and likely with syzkaller automation that creates kernel review changes from generated diffs.

## Risks And Edge Cases
The package has a hard-coded Gerrit host and scope. `CreateChange` computes a link even when posting fails, which may give callers a non-empty link with `changeID` zero. `request` reports response bodies on non-2xx errors, useful for diagnostics but potentially verbose. JSON marshal failures are unlikely because the request map contains simple types. There is no retry or rate-limit handling.

## Test Signals
Direct tests would need to inject HTTP or token sources, but the current code has fixed construction, so unit testing `request` is awkward without refactoring. Existing test coverage is focused on repository mapping in `repos_test.go`; integration testing would require real or fake Gerrit credentials.
