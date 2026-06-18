<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/sidecar.py -->
# Research: sources/storage-engines/foundationdb/packaging/docker/sidecar.py

## Purpose
Implements the Kubernetes container sidecar used to project config-map input, dynamic monitor configuration, binaries, and client libraries into a shared output directory for the main FoundationDB container. It can run once as an init container or stay up as an HTTP control server.

## Important APIs, Types, And Functions
`Config` parses CLI flags and legacy config/environment input, derives substitutions such as `FDB_PUBLIC_IP`, `FDB_MACHINE_ID`, `BINARY_DIR`, and TLS settings, and exposes `extract_desired_ip`. `SidecarHandler` implements `GET /ready`, `/substitutions`, `/check_hash/<file>`, `/is_present/<file>` and `POST /copy_files`, `/copy_binaries`, `/copy_libraries`, `/copy_monitor_conf`, `/refresh_certs`, `/restart`. Helpers include `is_path_allowed`, `check_hash`, `is_present`, `CertificateEventHandler`, and the copy functions.

## Control Flow
Startup constructs a singleton config, performs all copy operations, exits in `--init-mode`, or starts a threaded HTTP server. Requests first pass certificate authorization unless they are `/ready`; copy endpoints delegate to filesystem helpers; TLS mode wraps the socket and installs watchdog observers that reload the SSL context after certificate file changes.

## State And Persistence Behavior
Persistent effects are writes under `output_dir`: copied config files, dynamic `fdbmonitor.conf`, versioned binaries under `bin/<primary_version>`, and client libraries under `lib/` and `lib/multiversion/`. Writes use temporary files and `os.replace` for atomic replacement. The server keeps process-local SSL context state and reads `/var/fdb/version`.

## Dependencies And Integration Points
Uses Python stdlib HTTP, SSL, tempfile, pathlib, ipaddress, and `watchdog` observers. Integrated with FoundationDB Docker/Kubernetes images, config maps, TLS material mounted into pods, and the main container shared dynamic-conf volume.

## Risks And Edge Cases
Path containment uses `startswith` on absolute paths, which can be subtle for sibling prefixes; endpoint filenames should remain untrusted. Deprecated environment variables are rejected for newer versions but still honored for older versions. Certificate reload sleeps for 10 seconds and reload errors would surface in the observer thread. `POST /restart` exits the process intentionally.

## Test Signals
Covered by `sidecar_test.py` for HTTP readiness, substitutions, hash/presence checks, nested paths, outside-path rejection, and copy endpoint basics. TLS, certificate rule matching, watchdog reload, and binary/library copy paths need separate integration coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/sidecar.py -->
