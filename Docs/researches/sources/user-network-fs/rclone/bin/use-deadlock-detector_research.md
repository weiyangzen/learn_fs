# sources/user-network-fs/rclone/bin/use-deadlock-detector

Purpose: temporary debugging script that rewrites Go source to use `github.com/sasha-s/go-deadlock` mutex types. It refuses to run if tracked files have uncommitted changes, installs the dependency, replaces `sync.RWMutex` and `sync.Mutex` occurrences with `deadlock` equivalents, and runs `goimports`.

State changes are broad source rewrites, module changes from `go get`, and import formatting. Dependencies are git, Go, find, sed, xargs, and goimports. Risks are intentionally high: pattern replacement is broad, user must undo with `git reset --hard HEAD`, untracked/generated files are not checked, and it can affect comments or non-target contexts. Test signal is subsequent test runs under deadlock detector.
