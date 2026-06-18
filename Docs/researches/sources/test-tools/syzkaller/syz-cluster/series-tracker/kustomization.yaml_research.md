## sources/test-tools/syzkaller/syz-cluster/series-tracker/kustomization.yaml

This kustomization includes `deployment.yaml` and `git-pvc.yaml` for the series tracker. It is a simple resource aggregator; image substitutions and environment-specific storage changes are expected elsewhere.

There is no runtime state in the file. The main risk is that overlays must provide required global config and image values.
