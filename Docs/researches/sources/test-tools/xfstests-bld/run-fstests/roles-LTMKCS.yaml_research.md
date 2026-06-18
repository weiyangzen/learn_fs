# sources/test-tools/xfstests-bld/run-fstests/roles-LTMKCS.yaml

Purpose: custom Google Cloud IAM role for long-term monitoring (LTM) and kernel compile server (KCS) VMs. It grants permissions needed to manage compute resources, read images, manipulate instances/disks/networks, write logs, and interact with storage.

Important permissions: broad compute instance lifecycle operations, disk create/delete/resize/snapshot/update/use, image get/list/useReadOnly, network/subnetwork use and update, service account actAs/list/get, extensive logging permissions, project get, and storage object create/delete/get/list/update.

Control flow/state: declarative YAML for GCP custom role creation/update. Its effect persists in IAM and is consumed by service accounts used by LTM/KCS instances.

Dependencies/integration: supports `gce-xfstests launch-ltm`, `launch-kcs`, LTM batch submission, KCS build delegation, and VM self-management workflows.

Risks: very high privilege role, including instance create/delete/update, network mutation, storage delete, and service account actAs. A compromised LTM/KCS VM would have wide project impact. Scope should be isolated to a dedicated project where possible.

Test signals: LTM/KCS integration tests should verify required operations under this role; IAM recommender/policy analysis can identify unused permissions for reduction.
