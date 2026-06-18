# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-repo-cache

Purpose: provisions and mounts a persistent disk used as kernel compile/cache storage for KCS.

Important flow: source GCE and test config, define disk name `kcs-cache-disk`, by-id path `google-kcs-cache`, and default size 60 GB. If the disk does not exist, create it. Attach it to the current instance as `kcs-cache`, disable auto-delete, verify the device, format ext4 only on first creation, mount it at `/cache`, create `/cache/ccache`, and append `CCACHE_DIR=/cache/ccache` to root's shell profile.

State and dependencies: persistent GCE disk, `/cache`, `/cache/ccache`, and `/root/.bashrc`. It depends on `gcloud`, instance variables from `/root/test-config`, `mkfs.ext4`, and block device naming.

Integration points: KCS Git repositories live under `/cache/repositories` via the Go git utility, and build logs can use cache-backed ccache.

Risks and test signals: by-id device creation can lag after attach; the script exits immediately if not present. It appends to `.bashrc` every run. Tests should validate idempotent existing-disk attach and first-create formatting.
