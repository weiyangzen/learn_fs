## sources/test-tools/syzkaller/sys/fuchsia/fidlgen/main.go

Purpose: generation tool that invokes Fuchsia `fidlgen_syzkaller`, parses generated syz descriptions, prunes unused nodes, and writes per-library `.syz.txt` files atomically.

Important APIs/types/functions: `main` and `fidlgen`.

Control flow: `main` checks `TARGETOS`, `TARGETARCH`, and `SOURCEDIR`, resolves the Fuchsia build output and fidlgen binary, iterates `layout.AllFidlLibraries`, generates raw syz files from JSON IR, parses all `.txt` descriptions, collects unused nodes with the compiler, filters them, and rewrites each generated file with only relevant nodes. `fidlgen` validates JSON input, runs the external tool with a one-minute timeout, prints tool output, and returns the generated file path.

State and persistence: reads environment and Fuchsia build artifacts; writes `.syz.txt` files atomically in the working directory.

Dependencies/integration: depends on syzkaller AST/compiler packages, os utilities, tool failure handling, Fuchsia layout mapping, and target metadata.

Risks: silently returns when not building Fuchsia or `SOURCEDIR` is empty. External tool path and generated JSON paths are build-layout sensitive. Pruning correctness depends on compiler unused-node analysis.

Test signals: no direct tests in this subset; exercised by go generate and Fuchsia description generation workflows.
