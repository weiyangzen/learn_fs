# sources/security-integrity/fscrypt/tools.go

Purpose: This Go file is build-tagged as `tools`, so it is never compiled into fscrypt binaries. It records development tool dependencies as blank imports so Go module resolution keeps versions for `misspell`, `gocovmerge`, `goimports`, `protoc-gen-go`, and `staticcheck`.

Important APIs and functions: There are no runtime APIs. The only package-level behavior is dependency anchoring through blank imports.

Control flow and state: No control flow executes at runtime and no state is persisted by this file. Its effects are limited to module graph and developer tooling reproducibility.

Dependencies and integration points: It integrates with Go module tooling, CI linting, code generation, and coverage workflows.

Risks and test signals: The main risk is stale tool dependencies causing developer/CI drift. Test signal is indirect: `go mod tidy` should retain these tool modules when the tools build tag is considered.
