# sources/user-network-fs/rclone/Makefile

Purpose: Central build, test, lint, documentation, release, beta, upload, dependency, website, and Docker plugin automation for rclone.

Important APIs/types/functions: Variables derive branch, release tag, version, next versions, beta path/url, build tags, and ldflags embedding `fs.Version`. Core targets include `rclone`, `test_all`, `quicktest`, `racequicktest`, `compiletest`, `check`, dependency update targets, docs (`MANUAL`, commanddocs, backenddocs, rcdocs), install/clean/website/upload, release artifacts (`tarball`, `vendorball`, `sign_upload`, `check_sign`, `upload`, `upload_github`, `cross`, `beta`, `ci_upload`, `ci_beta`), development version bumps (`startdev`, `startstable`), and Docker plugin targets.

Control flow: Default `rclone` target builds with Go, embeds version via ldflags, handles Windows resources, and installs to `GOPATH/bin` atomically. CI targets wrap cross-compile and upload scripts. Documentation targets generate files from commands and content. Docker plugin targets build plugin rootfs and push/remove plugin images.

State and persistence: Writes binaries, build directories, docs outputs, release archives, checksums, tags, generated version files, and Docker plugin build directories. Some targets upload to configured remotes.

Dependencies and integration points: Integrates with Go, rclone's bin scripts, Hugo, pandoc, tidy, gpg, docker, cross-compile tooling, CI secrets/config, and Git.

Risks: Many targets have destructive or external side effects (`rm -rf`, uploads, git commits/tags, Docker pushes). Version derivation depends on git state and `VERSION`. Release targets assume external tools and remote configs.

Test signals: CI invokes `make`, `quicktest`, `racequicktest`, `compile_all`, `ci_beta`, `release_dep_linux`, Docker plugin targets, and docs/lint paths.
