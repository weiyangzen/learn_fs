# sources/test-tools/syzkaller/dashboard/config/openbsd/recreate.sh Research

## Purpose
This Bash script rebuilds the `ci-openbsd` Google Cloud instance image used by syzkaller OpenBSD CI. It creates a fresh OpenBSD GCE image, recreates the VM with the old IP and service account, rewrites SSH host keys, uploads worker disk/key artifacts, wires userspace directories, and reboots.

## Important commands and variables
- Uses `TODAY`, `SYZ_DIR`, `ZONE`, `INSTANCE`, `HOST`, `IP`, `SERVICE_ACCOUNT`, and `IMAGE` to derive cloud resource names.
- Calls `tools/create-openbsd-gce-ci.sh` and `tools/create-openbsd-vmm-worker.sh`.
- Uses `gcloud compute instances describe/delete/create`, `gcloud compute images delete/create`, and `gcloud storage cp`.
- Uses `ssh`/`scp` to halt/reboot and install worker artifacts.

## Control flow
The script verifies it is inside a syzkaller tree, discovers the current VM IP and service account, builds a tarball image, uploads it to GCS, halts and deletes/recreates image and VM resources, rewrites `~/.ssh/known_hosts`, builds worker artifacts, copies them to `/syzkaller/userspace`, creates a multicore userspace symlink set, then reboots. `set -eux` makes command failures stop execution except where explicit `|| true` handles expected missing resources.

## State and persistence
Persistent state lives in GCP images, VM instance metadata/disks/IPs, public GCS objects, local `known_hosts`, and remote `/syzkaller/userspace*` directories. The script drops generated files in the current directory.

## Dependencies and integration points
Depends on GCloud CLI auth for project `syzkaller`, SSH config/key material, GCE networking, `genisoimage`, `growisofs`, qemu/kvm, expect, and syzkaller tool scripts. It integrates with dashboard OpenBSD overlays and CI workers.

## Risks
It is destructive to the named VM/image, rewrites `~/.ssh/known_hosts`, assumes GCP project resource names and IP are reusable, and can leave partial cloud resources if interrupted after deletion. Running outside a temp directory may clutter the caller's current directory.

## Test signals
Dry-run style validation is limited because commands are side-effectful. Safer checks are shell syntax validation, confirming GCloud auth/project access, verifying tool scripts and artifacts exist, and post-run SSH/worker boot checks. No destructive command was run for this research.
