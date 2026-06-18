# sources/user-network-fs/rclone/backend/alias/alias.go

Purpose: Implements rclone's `alias` backend, a virtual provider that redirects an alias remote to another configured remote/path.

Important APIs/types/functions: Registers `fs.RegInfo{Name:"alias", NewFs: NewFs}` with required option `remote`. `Options` contains `Remote string`. `NewFs` parses config with `configstruct.Set`, validates non-empty remote, rejects aliases pointing at themselves with `strings.HasPrefix(opt.Remote, name+":")`, and returns `cache.Get(ctx, fspath.JoinRootPath(opt.Remote, root))`.

Control flow: When rclone opens `aliasName:some/root`, `NewFs` joins the configured target remote with the requested root and returns the actual wrapped Fs directly, not an alias wrapper type.

State and persistence: No backend state after construction; configuration persists in rclone config. Fs caching is delegated to `fs/cache`.

Dependencies and integration points: Depends on rclone core `fs`, `cache`, config mapping/struct parsing, and `fspath.JoinRootPath`. Integrates with all target backends because it returns the target Fs.

Risks: Self-reference check only detects direct `name:` prefix, not longer alias cycles. Errors from the target remote surface as alias creation errors. Returning the target Fs means alias identity/features are those of the target.

Test signals: `alias_internal_test.go` covers empty remote, invalid remote, root/list path joining, relative path behavior, and local backend listing.
