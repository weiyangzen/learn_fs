# sources/storage-engines/badger/badger/Makefile

Purpose: builds the Badger command-line binary for the current or supplied GOOS/GOARCH.

Important flow: defaults read `GOOS` and `GOARCH` from `go env`; `all` depends on `badger`; the `badger` target runs `go build --tags=jemalloc -o badger-$(GOOS)-$(GOARCH) .`.

State and persistence: output is a platform-named binary in the `badger` CLI directory. Dependencies are Go, module dependencies, and jemalloc build tags/library availability. Risks: always building with `jemalloc` tags can fail if the environment lacks the expected native library; output naming is platform-specific and release workflows assume these names. Test signals are cross-compilation workflow, release build workflow, and local `make -C badger badger`.
