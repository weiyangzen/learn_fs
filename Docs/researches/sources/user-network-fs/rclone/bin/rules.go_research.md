# sources/user-network-fs/rclone/bin/rules.go

Purpose: ruleguard custom lint rules for gocritic/golangci-lint. The `useFsLog` matcher suggests rewriting standard-library `log.Print/Fatal/Panic` calls to rclone `fs.Log/Fatal/Panic` variants, wrapping non-string variadic arguments with `fmt.Sprint` when needed.

State is declarative lint configuration only; it is excluded from normal builds with `//go:build ruleguard`. Dependencies are `github.com/quasilyte/go-ruleguard/dsl` and golangci-lint gocritic integration. Risks are documented in comments: cache invalidation is manual, suggestions can require import cleanup, and suggestions are wrong inside the `fs` package or in scopes where `fs`/`fmt` names collide. Test signal is lint execution; no standalone unit tests.
