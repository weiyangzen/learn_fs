# sources/sync-backup/restic/helpers/build-release-binaries/main.go

## Purpose

This Go helper builds restic release binaries for a matrix of target operating systems and architectures. It is intended to run in the release builder environment, producing named binaries or compressed archives under an output directory.

## Important APIs, Types, and Functions

- `opts` stores flags: verbose, source/output directories, extra build tags, platform subset, single platform, skip compression, and version.
- `init` registers pflag options.
- `die`, `msg`, and `verbose` print colored messages and handle fatal errors.
- Filesystem helpers: `rm`, `mkdir`, `abs`, `modTime`, `touch`, and `chmod`.
- `build(sourceDir, outputDir, goos, goarch)` invokes `go build` for `./cmd/restic` with `CGO_ENABLED=0`, `GOOS`, `GOARCH`, `-ldflags "-s -w"`, and tags `selfupdate,disable_grpc_modules` plus optional user tags. ARM builds set `GOARM=6`.
- `compress(goos, inputDir, filename)` creates `.zip` archives for Windows and `.bz2` for other platforms, then removes the uncompressed binary.
- `buildForTarget` builds, sets timestamps to the `VERSION` file modtime, chmods executable mode, and optionally compresses.
- `buildTargets` runs builds concurrently through an `errgroup` and job channel. Worker count is `GOMAXPROCS/4`, minimum one.
- `defaultBuildTargets` defines the release platform matrix.
- `downloadModules` runs `go mod download`.
- `selectSubset` splits the sorted platform list into deterministic `n/t` shards.
- `buildPlatformList` converts `os/arch` strings into the target map.
- `main` validates arguments, selects targets, prepares directories, downloads modules, and builds.

## Control Flow

The program parses flags at init. `main` rejects positional arguments, chooses the target matrix from defaults, `--platform-subset`, or `--platform`, resolves absolute source/output paths, creates the output directory, downloads modules, and starts concurrent builds. Each job builds a binary, normalizes its timestamp and executable mode, compresses it unless disabled, and logs duration.

## State and Persistence Behavior

Outputs are written to `opts.OutputDir`, default `/output`. Existing compressed output files for a target are removed before compression. Uncompressed binaries are removed after compression unless `--skip-compress` is set. Timestamps are set to match the source `VERSION` file to improve reproducibility. The helper also uses the Go module cache and reads source from `opts.SourceDir`.

## Dependencies and Integration Points

It depends on `go`, `zip`, `bzip2`, Go modules, pflag, and `golang.org/x/sync/errgroup`. It is called by `helpers/prepare-release/main.go` inside the `restic/builder` Docker container and by `helpers/verify-release-binaries.sh` to reproduce binaries. The build tag `disable_grpc_modules` is used to reduce binary size after Google Cloud Storage dependency changes.

## Risks and Edge Cases

- `errgroup.Wait()` result is ignored in `buildTargets`, but worker errors call `die` and exit the process, so normal errors do not propagate as Go errors.
- Map iteration order is nondeterministic for job scheduling, but `selectSubset` sorts platforms before slicing for deterministic sharding.
- Cross-platform reproducibility depends on builder image, Go version, module versions, compression tools, timestamps, and environment.
- `platform-subset` validation allows `total == 0` through until division would be unsafe; callers should pass valid `t/n` with `n > 0`.
- Windows ZIP uses `zip -q -X` to reduce metadata, while non-Windows uses bzip2.

## Test Signals

Release verification rebuilds with this helper and checks `SHA256SUMS`. A narrow smoke test is `go run helpers/build-release-binaries/main.go --platform linux/amd64 --output <dir> --source <repo>`.
