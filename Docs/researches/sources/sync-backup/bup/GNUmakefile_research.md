# sources/sync-backup/bup/GNUmakefile

## Purpose
Top-level GNU make build, install, test, documentation, cleanup, and compatibility target file for bup. It enforces GNU make 4.2+, records the make executable, includes configure output, builds C binaries/extensions, generates docs, prepares sample data, and runs tests/lint.

## Important APIs, Types, and Functions
Major targets are `all`, `install`, `check`, `dev-check`, `distcheck`, `long-check`, `Documentation/all`, `update-doc-branches`, `clean`, and legacy aliases. It builds `dev/python`, `dev/bup-exec`, `dev/bup-python`, `lib/cmd/bup`, and `lib/bup/_helpers$(soext)`.

## Control Flow
The file verifies make version, records `config/config.var/make`, includes `config/config.vars`, calculates OS/doc/sampledata settings, updates checkout info, compiles C objects with configured flags, validates the embedded Python launcher, and runs pytest with xdist derived from make parallelism.

## State and Persistence Behavior
Generated state includes `config/config.vars`, `config/config.h`, `config/config.var/*`, `lib/bup/checkout_info.py`, built binaries/shared objects, dependency `.d` files, docs, sampledata, `.pytest_cache`, and `test/tmp`. Install writes into `DESTDIR`-prefixed bin/lib/doc/man paths.

## Dependencies and Integration Points
Consumes `configure` outputs, platform prep scripts, `dev/refresh`, `dev/configure-sampledata`, C sources under `src/` and `lib/`, docs tooling (`pandoc`, `dot`), pytest, pylint, and shadow-bin to prevent accidental installed-bup use.

## Risks and Test Signals
Risks include stale configure state, wrong Python/readline flags, platform-specific shared-library extension mismatch, docs tool drift, cleanup of mounted test filesystems, and accidental local bup execution. Signals are successful `all`, `check`, `dev-check`, `clean`, generated dependency inclusion, shadow-bin assertion, and reproducible sampledata revision.
