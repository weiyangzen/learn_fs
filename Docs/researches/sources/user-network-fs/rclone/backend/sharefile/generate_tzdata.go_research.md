# sources/user-network-fs/rclone/backend/sharefile/generate_tzdata.go

Purpose: `go:build ignore` generator for embedding ShareFile timezone data into the `sharefile` package.

Important APIs/types/functions: `main` creates `AssetDir` from local `./tzdata` and calls `vfsgen.Generate` with package name `sharefile`, build tags `!dev`, and variable name `tzdata`.

Control flow: when invoked manually with `go run`, it reads the `tzdata` directory and generates Go source through `vfsgen`. On generation failure it logs fatally.

State and persistence behavior: produces generated files in the working directory according to `vfsgen` behavior. It is not part of normal builds due to the ignore build tag.

Dependencies/integration: depends on `github.com/shurcooL/vfsgen`, `net/http`, and `log`. It supports the ShareFile backend's timezone lookup assets.

Risks/test signals: generator assumes `./tzdata` relative to invocation directory. There are no tests in this subset; build/generation success is the validation path.
