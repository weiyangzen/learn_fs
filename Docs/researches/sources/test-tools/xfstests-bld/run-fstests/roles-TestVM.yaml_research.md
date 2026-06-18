# sources/test-tools/xfstests-bld/run-fstests/roles-TestVM.yaml

- Purpose: GCE IAM custom role for individual test VMs; it declares the permissions that launched test VMs receive for metadata, disks, logging, storage, and limited Compute API interactions. The file is 185 lines/5215 bytes and is researched as source path `sources/test-tools/xfstests-bld/run-fstests/roles-TestVM.yaml`.
- Important APIs/types/functions: YAML custom-role fields `stage`, `title`, `description`, and `includedPermissions`; permissions include compute.addresses.get, compute.addresses.list, compute.addresses.use, compute.addresses.useInternal, compute.diskTypes.get, compute.diskTypes.list, compute.disks.create, compute.disks.createSnapshot and 172 more entries.
- Control flow: declarative only; `gce-do-setup` passes it to `gcloud iam roles update --file` for the project-scoped role `forTestVM`.
- State and persistence: persists in GCP IAM, not in the repository at runtime; changes affect future launched test VMs after setup reruns.
- Dependencies/integration: consumed by setup scripts, GCE service accounts, metadata/storage/logging APIs, and Compute Engine disk/image operations used by test VMs.
- Risks and test signals: overly broad permissions increase blast radius, missing permissions break finalization/result upload; validate by rerunning setup and launching a smoke GCE test VM.
