# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-setup-filestore

Purpose: creates or discovers a Google Filestore NFS instance for NFS-backed xfstests and writes runtime mount parameters.

Important flow: describe configured Filestore instance; if missing, derive the VM network from instance JSON, create Filestore with configured size/tier/location and share name `nfstest`, then describe it again. Extract IP with `jq`, mount `ip:/nfstest` on `/mnt`, create per-instance `test` and `scratch` directories plus busy marker, unmount, and write `/run/filestore-param`.

State and dependencies: GCP Filestore instance, `/mnt/<instance>/test`, `/mnt/<instance>/scratch`, `/mnt/busy-<instance>`, and `/run/filestore-param`. Depends on `gcloud`, `jq`, NFS mount support, and config variables from `gce-setup`.

Integration points: `gce-setup` runs it on first boot and reboot remount; `gce-shutdown` reads `/run/filestore-param` to remove per-instance directories and delete Filestore when no busy markers remain.

Risks and test signals: create/describe operations are synchronous and can fail due to quota or network readiness. Busy markers are best-effort coordination. Tests should verify param file content and cleanup interaction with shutdown.
