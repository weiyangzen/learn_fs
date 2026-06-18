# sources/test-tools/syzkaller/syz-cluster/dashboard/deployment.yaml

Purpose: Kubernetes deployment for syz-cluster web dashboard.

Important APIs/types/functions: `Deployment` `web-dashboard`, one replica, service account `gke-service-ksa`, env/config mounts, container port 8081, resource requests/limits.

Control flow: runs `${IMAGE_PREFIX}web-dashboard:${IMAGE_TAG}` with config map mounted at `/config` and global config env injected.

State and persistence: no local persistence; reads backend config and serves UI.

Dependencies and integration points: relies on external service account and ConfigMaps from overlays.

Risks: no Service in this subset; exposure likely handled elsewhere. Resource limits should match expected dashboard workload.

Test signals: pod readiness and dashboard HTTP response on port 8081.
