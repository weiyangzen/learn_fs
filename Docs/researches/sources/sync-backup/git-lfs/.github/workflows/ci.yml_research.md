# sources/sync-backup/git-lfs/.github/workflows/ci.yml

Purpose: comprehensive GitHub Actions CI for git-lfs covering default Go/Git builds, specific Go version, Windows packaging, latest and earliest Git compatibility, and Docker package builds including ARM.

Important APIs/types/functions: trigger `on: [push, pull_request]`, `GOTOOLCHAIN=local`, jobs `build-default`, `build-go`, `build-windows`, `build-latest`, `build-earliest`, `build-docker`, and `build-docker-arm`; Actions `checkout@v6`, `setup-go@v6`, artifact upload, Git for Windows SDK setup, and scripts `script/cibuild`, `script/build-git`, docker build scripts, and Makefile release/package targets.

Control flow: matrix default builds run on Ubuntu and macOS with Go 1.26, run cibuild, build release assets, and upload OS artifacts. A Go 1.25 Ubuntu job checks compatibility. Windows installs Asciidoctor, Go, InnoSetup, Git SDK, builds/test, then creates x86, x64, and arm64 executables plus installer assets. Latest/earliest Git jobs build Git from source on Ubuntu/macOS and run cibuild, with latest also testing SHA-256 repositories. Docker jobs build package containers for x86 and ARM.

State/persistence behavior: CI produces artifacts under `bin/assets`, modifies generated man content during Windows builds, clones Git and build-docker repositories into `$HOME`, and uploads build artifacts. No repo commits are made.

Dependencies/integration: depends on Ruby gems, Go toolchains, GNU gettext/libarchive tools, Chocolatey packages, Git for Windows SDK, external Git source, and git-lfs docker packaging scripts.

Risks/test signals: broad external dependencies make CI sensitive to runner image, Go version, Git source, Chocolatey, and docker image changes. Test signals are matrix pass/fail, uploaded assets per OS, Windows cross-arch binary creation, SHA-256 Git compatibility, earliest Git compatibility, and docker packaging success.
