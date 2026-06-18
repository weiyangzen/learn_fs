# sources/sync-backup/syncthing/build.go

Purpose: Go-based build orchestration tool for Syncthing. It centralizes target metadata, builds, installs, tests, benchmarks, integration tests, asset/protobuf/mock generation, translations, packaging, Debian package creation, version metadata, code signing, archives, dependency updates, and changelog extraction.

Important APIs/types/functions: `target` describes binaries, Debian names/dependencies/scripts, build packages, archive files, systemd service, install files, and build tags. `archiveFile` carries source, destination, and permissions. `targets` covers `syncthing`, `stdiscosrv`, `strelaysrv`, infrastructure services, and `all`. Major functions include `initTargets`, `runCommand`, `parseFlags`, `test`, `bench`, `integration`, `install`, `build`, `appendParameters`, `buildTar`, `buildZip`, `buildDeb`, `shouldBuildSyso`, `copyFile`, `rebuildAssets`, `lazyRebuildAssets`, `updateDependencies`, `proto`, `translate`, `ldflags`, `getVersion`, `getGitVersion`, `buildStamp`, archive writers, signing helpers, and changelog helpers.

Control flow: `main` parses flags, initializes targets, defaults to `install all` with no args, otherwise executes a command for an explicit or default `syncthing` target. Build/test paths regenerate assets lazily, set `GOOS`, `GOARCH`, and `CC`, append tags/race/pkgdir/install-suffix/ldflags, and invoke external commands. Packaging builds binaries, optionally signs, rewrites archive paths, emits tar/zip/deb artifacts, and writes compatibility JSON for archive builds.

State and persistence behavior: writes binaries, `bin`, `deb`, archives, generated assets, generated protobuf/mock files, `compat.json`, Windows `versioninfo.json`/`resource.syso`, translations, and Debian maintainer scripts. Version state comes from `VERSION`, `RELEASE`, Git tags/describe/branch, build timestamp, user, host, tags, and `EXTRA_LDFLAGS`.

Dependencies/integration: wraps Go toolchain, Git, Buf, fpm, goversioninfo, codesign/security, translation scripts, Weblate/Transifex scripts, release compatibility YAML, and package-specific files under `etc`, `extra`, `man`, `assets`, and `cmd`.

Risks/test signals: many commands call `log.Fatal`, making partial generated files possible on failure. Version derivation and Debian arch normalization are release-sensitive. Zip text files get CRLF conversion while binaries copy verbatim. Strong signals are `go run build.go`, `go run build.go test`, packaging jobs, meta lint, and release workflow artifacts.
