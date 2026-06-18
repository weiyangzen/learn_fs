# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/gcp/config.go

Purpose: parses GCE, LTM, and KCS shell-style config files into thread-safe key/value maps.

Important APIs/state: `Config` wraps `kv`; globals `GceConfig`, `LTMConfig`, `KCSConfig`, paths for appliance config and generated instance configs, and `configLock`. `init` loads `/usr/local/lib/gce_xfstests.config`, derives project-specific `.ltm_instance_*` and `.kcs_instance_*` paths, and optionally loads them. `Update` refreshes all available configs. `Get(configFile)` parses a file; `(*Config).Get(key)` returns a value or error.

Parsing behavior: regex accepts lines like `declare -- KEY="value"`, `declare -x KEY="value"`, and `KEY=value`. It ignores malformed lines and keeps quotes in simple assignment values when the file includes them.

State and dependencies: reads config files from fixed appliance paths; guarded by RW mutex; depends on `check.ReadLines`.

Risks and test signals: regex only captures non-whitespace values for declare lines, so values with spaces are ignored/truncated. `Get` takes a read lock on the same global lock even for independent config objects. Tests cover accepted/ignored line forms and empty values.
