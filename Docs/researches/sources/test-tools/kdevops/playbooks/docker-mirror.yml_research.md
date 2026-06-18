# sources/test-tools/kdevops/playbooks/docker-mirror.yml

Purpose: installs and manages a local Docker image mirror using the docker-mirror role.

Important APIs/types/functions: localhost play with `become: true`, optional `include_vars` from extra vars using `with_first_found`, and `include_role` for `docker-mirror`. Tags include `docker-mirror`, `docker-mirror-pull`, and `docker-mirror-status`.

Control flow: load optional extra variables, then include the role under tag control so callers can install, pull, or inspect mirror state.

State/persistence behavior: the role likely creates local mirror containers, storage, systemd units, or cached images on localhost.

Dependencies/integration: used by linux mirror/cache infrastructure and any workflow that benefits from local Docker pull caching.

Risks/test signals: optional vars are ignored on missing file, so defaults must be safe. Test signals are role idempotence, reachable mirror endpoint, and tag-specific role behavior.
