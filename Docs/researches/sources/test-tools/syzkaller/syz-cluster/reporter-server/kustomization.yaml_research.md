## sources/test-tools/syzkaller/syz-cluster/reporter-server/kustomization.yaml

This kustomization includes `deployment.yaml` and `service.yaml` for reporter-server. It has no patches, generators, or image transformations locally, so environment-specific substitutions must happen in parent overlays or build tooling.

The file is an integration manifest with no runtime state. Risk is mainly omission: if parent overlays do not inject `${IMAGE_PREFIX}`/`${IMAGE_TAG}` or config maps, deployment manifests remain templated.
