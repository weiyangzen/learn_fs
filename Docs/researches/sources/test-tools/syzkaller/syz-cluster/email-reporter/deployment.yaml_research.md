# sources/test-tools/syzkaller/syz-cluster/email-reporter/deployment.yaml

## Purpose
Defines the Kubernetes deployment for the email reporter service.

## Important APIs, types, and functions
Creates an `apps/v1` `Deployment` named `email-reporter` with one replica and pods labeled `app: email-reporter`. It uses service account `gke-email-reporter-ksa`, image `${IMAGE_PREFIX}email-reporter:${IMAGE_TAG}`, config volume from `global-config`, and PVC `reporter-lore-disk-claim` mounted at `/lore-repo`. Resource requests are 2 CPU/8G and limits are 4 CPU/16G.

## Control flow
Kubernetes maintains exactly one replica, matching the application comment that only one copy should run at the same time. The pod reads config from `/config` and persists the Lore checkout under `/lore-repo`.

## State and persistence behavior
Durable state is external: Spanner/report APIs for report state and the PVC for Lore repository checkout. The deployment itself does not define probes.

## Dependencies and integration points
Depends on `global-config`, `reporter-lore-disk-claim`, and the GKE service account expected from Terraform. Network policies allow it to contact controller, reporter-server, and the internet/email/git paths.

## Risks and edge cases
The deployment is annotated to ignore kube-linter's non-existent service account warning because Terraform owns the account. Running more than one replica risks duplicate polling/sending despite report confirmation safeguards. Lack of probes means Kubernetes only sees process liveness.

## Test signals
Go tests cover report and incoming email flow. Local or cluster deployment tests would be needed to catch volume/config/service-account regressions.
