## sources/test-tools/syzkaller/syz-cluster/tools/db-mgmt/migrate-job.yaml

This Kubernetes `Job` runs `db-mgmt migrate` with service account `gke-db-admin-ksa`, environment from `global-config-env`, zero retries, and one-day TTL after finish. It uses image `${IMAGE_PREFIX}db-mgmt:${IMAGE_TAG}`.

Integration is with deployment/migration operations and Terraform-defined service accounts. Risks include `backoffLimit: 0` requiring manual rerun on transient errors and templated image variables requiring overlay substitution.
