<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/Makefile -->
# sources/test-tools/kdevops/workflows/rcloud/Makefile

## Purpose
This Makefile integrates rcloud into the kdevops build and operations surface. When `CONFIG_RCLOUD=y`, it builds the Rust server, optionally builds and installs the Terraform provider, prepares guestfs base images, installs the service via Ansible, starts systemd, and provides status/help targets.

## Important Targets and Variables
`RCLOUD_WORKFLOW := workflows/rcloud`. `RCLOUD_PORT` is extracted from `CONFIG_RCLOUD_SERVER_BIND`. `rcloud-check-deps` verifies `cargo`, `rustc`, `pkg-config`, and libvirt development libraries. The release binary target runs `cargo build --release`. `rcloud-check-go-deps` and `terraform-provider-rcloud/terraform-provider-rcloud` are active when `CONFIG_RCLOUD_ENABLE_TERRAFORM_PROVIDER=y`. Operational targets include `rcloud-build`, `rcloud-base-images`, `rcloud`, `rcloud-status`, provider installation targets, and help text.

## Control Flow
Enabling rcloud appends `rcloud-build` to `DEFAULT_DEPS`. The install path first builds dependencies, then runs `playbooks/guestfs.yml` for base images, then `playbooks/rcloud.yml`, optionally copies the Terraform provider into `~/.terraform.d/plugins`, starts `rcloud` with systemd, and invokes `scripts/check-health.py`.

## State, Persistence, and Dependencies
Build state lives under `workflows/rcloud/target/release`. Provider state is copied into the user's Terraform plugin directory. Runtime state is managed by systemd, libvirt, guestfs image directories, and Ansible inventory. The Makefile depends on cargo/rustc/pkg-config/libvirt, optionally Go, Ansible, sudo/systemd, and the rcloud health script.

## Risks and Test Signals
The Makefile shell-extracts the port with `sed`, which assumes a simple `host:port` bind string. The install target starts a system service and copies files into the user's home, so dry-run separation matters. Health-check success after systemd start is the strongest integration signal; build-only validation is `rcloud-build`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/Makefile -->
