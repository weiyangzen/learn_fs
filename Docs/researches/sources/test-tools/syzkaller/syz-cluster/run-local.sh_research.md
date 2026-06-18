## sources/test-tools/syzkaller/syz-cluster/run-local.sh

`run-local.sh` is a helper for running a named local image in minikube. It requires the first argument as command/service image name, deletes any previous `run-local` pod, then runs `local/<name>` with `image-pull-policy=Never`, Spanner emulator env vars, local blob storage path, label `app=db-mgmt`, and attaches with `--rm`.

State is transient Kubernetes pod state. It integrates with minikube, local cluster overlays, the Spanner emulator service, and locally built syz-cluster images. Risks include the `kubectl` alias only applying in this script shell, fixed env/config values, label always being `app=db-mgmt` regardless of image, and a typo in the cleanup comment.
