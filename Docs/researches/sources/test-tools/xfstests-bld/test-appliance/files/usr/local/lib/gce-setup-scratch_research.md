# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-setup-scratch

Purpose: provisions the scratch/test block storage layout for GCE xfstests.

Important flow: prefer local SSD/NVMe devices, otherwise parse `DISK_SPEC` for scope, disk type, and size; create zonal or regional PD with replica zones; attach as `scratch`; set auto-delete; verify by-id device. In blktests mode it exits after attach. Otherwise, if volume group `xt` does not exist, create PV/VG and logical volumes `vdb`, `vdc`, `vdd`, `vde`, `vdf`, `vdi`, and `vdj` according to computed sizes, formatting `vdb` ext4 for primary test use.

State and dependencies: GCE disk `${instance}-scratch`, `/dev/disk/by-id/google-scratch`, LVM VG `xt`, logical volumes under `/dev/mapper/xt-*`. Depends on `gcloud`, `pvcreate`, `vgcreate`, `lvcreate`, `mke2fs`, config/env from `gce-setup`.

Integration points: sizes come from `compute_partition_sizes` in `gce-setup`; `/root/test-config` maps test devices through `/dev/mapper/xt-*`.

Risks and test signals: parsing `DISK_SPEC` is permissive and silently falls back. Regional disk zone selection is heuristic. Existing VG prevents resizing/recreation. Tests should cover zonal/regional parsing, local SSD preference, and LVM idempotence.
