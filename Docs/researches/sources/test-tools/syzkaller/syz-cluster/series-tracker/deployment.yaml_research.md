## sources/test-tools/syzkaller/syz-cluster/series-tracker/deployment.yaml

This deployment runs one `series-tracker` pod. It mounts a persistent volume at `/git-repo` for polled lore git archives and `global-config` at `/config`, using image `${IMAGE_PREFIX}series-tracker:${IMAGE_TAG}` and large CPU/memory requests.

The pod has no explicit envFrom in this file, so config is expected via mounted files or app defaults. Integration points are the PVC, global config, and controller API upload endpoints. Risks include single-replica polling, persistent repo corruption/size growth, and templated image variables requiring overlay substitution.
