# sources/sync-backup/git-lfs/lfshttp/endpoint.go

Purpose: Defines endpoint metadata and URL conversion helpers for HTTP, SSH, bare SSH, local path, and file URL remotes.

Important APIs/types/functions: `Endpoint`, `UrlUnknown`, `endpointOperation`, `EndpointFromSshUrl`, `EndpointFromBareSshUrl`, `EndpointFromHttpUrl`, `EndpointFromLocalPath`, and `EndpointFromFileUrl`.

Control flow: SSH URL parsing extracts user/host, optional port, path, original URL, and derives an HTTPS fallback URL. Bare SSH URLs are rewritten to `ssh://` form, supporting bracketed host:port. HTTP and file URLs pass through. Local paths are rewritten through Git path helpers.

State and persistence behavior: Pure value construction; no state persists.

Dependencies and integration points: Used by `lfsapi.EndpointFinder` and `lfshttp.Client.NewRequest`. Integrates with `ssh.SSHMetadata` and `git.RewriteLocalPathAsURL`.

Risks and edge cases: Bare SSH parsing uses colon splitting and special handling for bracketed ports; unusual paths containing additional colons may be fragile. Invalid SSH hosts yield `UrlUnknown`.

Test signals: Covered extensively by `endpoint_finder_test.go` through endpoint parsing and suffix derivation.
