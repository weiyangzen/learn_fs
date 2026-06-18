# sources/storage-engines/foundationdb/packaging/docker/Dockerfile

Purpose: This multi-stage Dockerfile builds the family of FoundationDB container images: base tools, Go build stages, AWS S3 credentials sidecar, FoundationDB runtime, Kubernetes monitor, Kubernetes sidecar, Mako, and YCSB runner.

Important stages: `base` installs Rocky Linux troubleshooting tools and verified `tini`; `go-build` builds `fdb-kubernetes-monitor`; `go-credentials-fetcher-build` builds the S3 credential fetcher; `foundationdb-base` creates user `fdb`, downloads FoundationDB binaries and client libraries for `TARGETARCH`, and sets multiversion library layout. Later targets add monitor entrypoints, sidecar Python/watchdog support, runtime scripts, FlameGraph tools, Mako, Java/kubectl/AWS CLI, and YCSB.

Control flow: Build args choose FoundationDB version, library versions, website URL, and architecture. Architecture branches map Docker `amd64`/`arm64` to release artifact names. Several downloads are checksum-verified before installation.

State and persistence behavior: Images persist binaries, scripts, `/var/fdb` directory structure, multiversion client libraries, environment defaults, and declared volumes for data/input/output/logs. Runtime containers write cluster files, data, logs, trace logs, or credential files depending on target.

Dependencies and integration points: It integrates GitHub release artifacts, local `website` build context, Go sources, sidecar scripts, `fdb.bash`, `run_ycsb.sh`, Kubernetes monitor config, AWS CLI, and YCSB FoundationDB binding.

Risks: External pinned downloads can break or become stale; Python 3.9 sidecar has an explicit EOL note. `foundationdb-base` copies client libraries into both `/usr/lib/fdb/multiversion` and `/var/fdb/lib`, so version layout must match clients. Tests should build all targets for both architectures, verify checksums, run `fdbserver`/`fdbcli`, start sidecars, and execute YCSB smoke workloads.
