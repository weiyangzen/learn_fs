# sources/test-tools/kdevops/playbooks/rcloud.yml

Purpose: Installs and configures the `rcloud` REST API server as a systemd service on localhost for kdevops VM management.

Key APIs and flow: The play validates that the Rust-built `workflows/rcloud/target/release/rcloud` binary exists, copies it to `/usr/local/bin`, creates a system user and `/etc/rcloud`, writes `/etc/systemd/system/rcloud.service`, adds the service user to the libvirt qemu group, reloads systemd, enables the service, derives a port from `rcloud_server_bind`, and prints health-check commands.

State, dependencies, integration: Mutates host system paths, users, groups, and systemd state. The service depends on libvirtd and environment variables such as `KDEVOPS_ROOT`, storage pool path, base images directory, libvirt URI, and bridge name.

Risks and test signals: It enables but does not start the service; port extraction assumes `host:port`; hardening read/write paths must match storage layout; group name defaults may vary by distro. Tests should run Ansible check mode where possible and validate rendered service content.
