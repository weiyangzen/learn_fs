<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/Makefile -->
# sources/sync-backup/git-lfs/Makefile

Purpose: top-level build, test, localization, documentation, and release orchestration for the Git LFS Go project. It defines how binaries, generated command manpage content, translation bundles, release archives, vendor archives, Windows/macOS signing assets, Go tests, integration tests, formatting, linting, and manpage outputs are produced.

Important APIs/types/functions: Make variables `GIT_LFS_SHA`, `VERSION`, `PREFIX`, `GO`, `GOTOOLCHAIN`, `LD_FLAGS`, `GC_FLAGS`, `BUILD`, `BUILD_TARGETS`, `RELEASE_TARGETS`, `MAN_ROFF_TARGETS`, `MAN_HTML_TARGETS`, and tools such as `go generate`, `go build`, `go test`, `goimports`, `asciidoctor`, `msgfmt`, `xgotext`, `tar`, `bsdtar`, `codesign`, and `signtool`. Key targets include `mangen`, `trgen`, `all`, `build`, platform-specific `bin/git-lfs-*`, `resource.syso`, `release`, `release-linux`, Windows staged release targets, `release-darwin`, certificate helpers, `test`, `integration`, `vendor`, `fmt`, `lint`, and `man`.

Control flow: source and version variables feed a reusable `BUILD` macro; generated manpage and translation Go files are prerequisites of binary targets; platform targets set `GOOS` and `GOARCH`; release archive targets wrap built binaries with README, changelog, manpages, and install scripts; Windows and Darwin release paths add platform-specific signing/notarization stages; `test` first builds/formats, creates an isolated temporary HOME and Git config environment, then runs package tests; `man` uses Asciidoctor to convert each `.adoc` page to roff and HTML.

State and persistence behavior: outputs are written under `bin/`, `bin/releases/`, `commands/mancontent_gen.go`, `tr/tr_gen.go`, `po/build`, `resource.syso`, `tmp/stage*`, `vendor/`, `man/`, and `go.sum`. Release targets package repository state at `$(VERSION)`, and code-signing/notarization targets depend on external keychain or certificate state.

Dependencies/integration points: integrates Go modules, vendoring, gettext catalogs, Asciidoctor extensions, Docker packaging scripts, Windows Inno Setup, macOS keychain/notarization helpers, Git archive, Git describe/rev-parse, and package lists mirrored to repository layout.

Risks and test signals: risks include stale generated mancontent/translations, missing optional local tools causing skipped localization or formatting, fragile tar transform differences between GNU and BSD tar, platform-only signing assumptions, duplicated `git` package in `PKGS`, and release artifact naming coupled to `VERSION`. Test signals are successful default `make`, `make test`, package-scoped `PKGS=... test`, generated manpages, release archive contents with correct prefixes, and Windows/Darwin release dry-runs in the intended host environments.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/Makefile -->
