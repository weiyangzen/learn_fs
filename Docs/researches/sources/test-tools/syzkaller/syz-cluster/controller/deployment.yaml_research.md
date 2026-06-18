# sources/test-tools/syzkaller/syz-cluster/controller/deployment.yaml

Purpose: Kubernetes deployment for syz-cluster controller API/processor.

Important APIs/types/functions: `Deployment` `controller-deployment`, one replica, service account `gke-service-ksa`, config env/map, port 8080, resource requests/limits.

Control flow: starts `${IMAGE_PREFIX}controller:${IMAGE_TAG}` with config mounted at `/config` and env from `global-config-env`.

State and persistence: controller persists through configured Spanner/blob services, not pod filesystem.

Dependencies and integration points: service account defined outside manifest, ConfigMaps from overlays, service in `service.yaml`.

Risks: single replica matches code comment that only one controller should run. Running more replicas could duplicate workflow/session processing.

Test signals: deployment readiness and service/API health.
