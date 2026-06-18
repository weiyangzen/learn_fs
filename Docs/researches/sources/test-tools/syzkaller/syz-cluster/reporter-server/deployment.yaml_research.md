## sources/test-tools/syzkaller/syz-cluster/reporter-server/deployment.yaml

This Kubernetes deployment runs one `reporter-server` pod. It uses Terraform-defined `gke-service-ksa`, image `${IMAGE_PREFIX}reporter-server:${IMAGE_TAG}`, config-map environment from `global-config-env`, and mounts `global-config` at `/config`.

The pod exposes container port 8080 and requests/limits relatively large CPU and memory. Integration points are `reporter-server/service.yaml`, global config overlays, Spanner/blob/email configuration via env/config, and the reporter API/generator process. Risks include single replica availability, service account external definition, and high static resource requests.
