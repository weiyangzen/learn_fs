# File Research: sources/virtualization/nbdkit/plugins/golang/Makefile.am

This Automake file builds the Go plugin binding examples and documentation.

Key behavior:
- Defines shared Go binding sources under `src/libguestfs.org/nbdkit`.
- Distributes binding sources, test helper, example plugins, Go modules, and POD docs.
- When Go is available, builds four example plugins with `go build -buildmode=c-shared`.
- Sets `PKG_CONFIG_PATH` so cgo finds the built nbdkit package metadata.
- Runs `dump-plugin-examples.sh` as the test.
- If POD tooling is available, builds `nbdkit-golang-plugin.3`.

Integration:
- The binding package is not built separately; it is compiled into each example shared library.
- Clean rules remove generated example `.so` and `.h` files.
