# sources/sync-backup/syncthing/.github/regsync.yml

Purpose: regclient/regsync configuration for mirroring Syncthing container images from GHCR to Docker Hub.

Important APIs/types/functions: `creds` reads Docker Hub username/token from environment template functions. `defaults` sets rate-limit minimum, retry interval, and parallelism. Three `sync` entries mirror `ghcr.io/syncthing/syncthing`, `ghcr.io/syncthing/relaysrv`, and `ghcr.io/syncthing/discosrv` to matching Docker Hub repositories, allowing tags `latest`, `rc`, `edge`, major, major.minor, semver, and rc semver patterns.

Control flow: the `docker-hub` job runs regsync once with this file after GHCR images are built. Regsync authenticates, lists allowed tags, and copies matching manifests/layers.

State and persistence behavior: registry state changes on Docker Hub; no repository-local state is written.

Dependencies/integration: depends on Docker Hub credentials, GHCR image publication, and `docker://docker.io/regclient/regsync:latest`.

Risks/test signals: permissive numeric regexes can mirror broad major/minor tags intentionally, while missing tags would leave Docker Hub stale. Test signals are successful sync logs and Docker Hub tags matching GHCR for releases/nightlies/edge.
