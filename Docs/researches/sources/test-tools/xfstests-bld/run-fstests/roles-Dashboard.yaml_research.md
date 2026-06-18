# sources/test-tools/xfstests-bld/run-fstests/roles-Dashboard.yaml

Purpose: custom Google Cloud IAM role definition for dashboard-related deployment/runtime. It grants a broad set of Compute, IAM, Logging, Recommender, Resource Manager, Cloud Run, and Storage permissions.

Important fields: `stage: ALPHA`, title/description, and `includedPermissions`. Notable capabilities include compute instance/disk/image/network inspection and mutation, service account listing/actAs, extensive logging access, Cloud Run service/revision/route reads, and storage object create/delete/get/list/update.

Control flow/state: declarative YAML; applied by gcloud/IAM tooling to create or update a custom role. Persistent state lives in GCP IAM.

Dependencies/integration: supports the xfstests dashboard and related launch utilities that need Cloud Run, storage, logging, and compute visibility.

Risks: permission set is very broad for a dashboard role, including many mutating Compute and Logging operations plus storage delete. Principle-of-least-privilege review is warranted before production use.

Test signals: deployment should verify the dashboard can sync/read results and serve without requiring unused mutation permissions; IAM policy simulator can reduce scope.
