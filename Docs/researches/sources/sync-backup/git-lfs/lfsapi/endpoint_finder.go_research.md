# sources/sync-backup/git-lfs/lfsapi/endpoint_finder.go

Purpose: Resolves LFS API endpoints and access modes from Git config, remotes, push URLs, aliases, local paths, FETCH_HEAD, and URL schemes.

Important APIs/types/functions: `EndpointFinder`, `endpointGitFinder`, `NewEndpointFinder`, `Endpoint`, `RemoteEndpoint`, `GitRemoteURL`, `NewEndpointFromCloneURL`, `NewEndpoint`, `AccessFor`, `SetAccess`, `ReplaceUrlAlias`, `ExtractRemoteUrl`, and alias helpers.

Control flow: Endpoint resolution prefers `lfs.pushurl` for uploads, then `lfs.url`, then remote-specific LFS URLs, Git remote URLs, and finally `FETCH_HEAD` for default remote downloads. Clone URLs are converted to endpoint URLs by appending `.git/info/lfs` or `/info/lfs` unless file URLs are used.

State and persistence behavior: Caches remotes, aliases, push aliases, and per-URL access modes. `SetAccess` writes or unsets `lfs.<url>.access` in the Git config and updates the access cache under lock.

Dependencies and integration points: Uses `git.Configuration`, `config.URLConfig`, Git remotes, `lfshttp.Endpoint` constructors, `creds.Access`, and SSH metadata parsing.

Risks and edge cases: URL alias matching intends longest prefix selection but compares strings lexicographically rather than length, which may matter for overlapping aliases. `ExtractRemoteUrl` has a restrictive regex. Local path detection depends on `os.Stat`.

Test signals: `endpoint_finder_test.go` broadly covers config precedence, SSH/HTTP/git/file/local paths, access config, alias replacement, FETCH_HEAD extraction helper, custom git protocol, and URL parsing cases.
