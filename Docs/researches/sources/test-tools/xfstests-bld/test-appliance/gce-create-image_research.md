# sources/test-tools/xfstests-bld/test-appliance/gce-create-image

Purpose: host-side GCE image creation orchestrator. It stages appliance payloads in GCS, launches a temporary build VM with startup metadata, waits for the VM to shut itself down, and creates a reusable GCE image from the boot disk.

Important flow: source run-fstests config/image/arch helpers; require `GS_BUCKET`, `GCE_PROJECT`, and `GCE_ZONE`; parse arch, distro, datecode, root FS family, packages, and Phoronix version; select Debian suite/image/backport package variables; stage `xfstests.tar.gz`, templated `gce-xfstests-bld.sh`, `files.tar.gz`, and run-fstests helper payloads; update `git-versions`; sync create-image payloads and debs to GCS; delete old build instance/disk; create build VM with startup-script-url metadata; wait until the instance disappears; create an image from the preserved boot disk and list images.

State and dependencies: temporary directory under `/tmp`, GCS `create-image/` and `debs/`, temporary GCE instance/disk `xfstests-bld`, final image family/name, labels from git versions. Depends on gcloud wrappers, tar, gzip/pigz, sed templating, run-fstests utilities, and local build artifacts.

Integration points: feeds `gce-xfstests-bld.sh` as startup script and installs the files that become the test appliance.

Risks and test signals: destructive cleanup deletes same-named build instances/disks. Template substitution is sed-based and sensitive to special characters in package lists. End-to-end validation is a bootable image and successful appliance self-deletion.
