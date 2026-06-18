# sources/sync-backup/unison/.github/workflows/CI.yml

Purpose: primary GitHub Actions CI/release workflow for Unison on pull requests and pushes. It builds docs, native/text/GUI binaries, package artifacts, release uploads, RPC ABI compatibility tests, dune builds, bytecode builds, and older-compiler compatibility builds.

Important jobs: `docs` builds manual artifacts with OCaml 4.14, HeVeA, lynx, and TeX; `build` runs a platform matrix across macOS, Ubuntu, Windows MinGW/MSVC, i386 variants, OCaml 4.14 and 5.x, packages binaries, and optionally publishes release assets; `rpc_abicheck` checks new/old client/server interoperability against tagged versions; `opam_dune_build` verifies dune/opam packaging; `bytecode_build` validates non-native builds; `build_compat` covers older OCaml and static/musl packaging.

Control flow: `build` depends on `docs` but runs even if docs failed via `if: !cancelled()`. A `vars` step derives executable suffixes, Windows architecture, staging paths, ref/tag metadata, package names, compression commands, and make implementation. Platform-specific sections install multilib, GTK, lablgtk, patch Windows MSVC opam packages, build `tui fsmonitor`, run self-tests over sockets, build GUI/mac UI, stage docs, strip binaries, collect DLLs/framework support files, package, upload artifacts, and publish tagged releases.

State/persistence: creates `_staging`, package directories, `pkg`, `_new`, `_prev`, local sockets, test backup dirs, GTK cache, `_opampkgs`, generated archives, and GitHub artifacts/releases.

Dependencies/integration: uses `actions/checkout`, `ocaml/setup-ocaml`, cache, upload/download-artifact, setup-python, `softprops/action-gh-release`, OS package managers, opam, make/nmake, lablgtk3, gvsbuild, dumpbin/objdump, and Unison self-tests.

Risks: high matrix complexity and many pinned workarounds for runner, opam, GTK, cairo, pkg-config, MSVC, and MinGW behavior. Release gating relies on tag parsing and `publish` matrix flags. Windows GTK packaging is fragile because dependency discovery and architecture selection depend on PATH ordering. The RPC compatibility patching embeds historical source diffs that can drift.

Test signals: successful docs artifacts, `make test`, local/RPC self-tests, GUI build completion, package creation, artifact uploads, ABI smoke tests in both client/server directions, dune build, bytecode test run, and release upload on version tags.
