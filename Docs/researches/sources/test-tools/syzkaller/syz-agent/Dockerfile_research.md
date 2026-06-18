# sources/test-tools/syzkaller/syz-agent/Dockerfile

Purpose: builds the production syz-agent container image.

Important APIs/types/functions: multi-stage Dockerfile with `syz-agent-builder` based on `gcr.io/syzkaller/env` and runtime based on `gcr.io/syzkaller/syzbot`.

Control flow: downloads Go modules, copies source, injects revision args, builds linux amd64/arm64 targets and agent binary, then copies binaries/sys metadata into runtime image. Runtime image installs git safe-directory config, downloads/decompresses buildroot images and kernel configs, copies `git-cookie-authdaemon` and `run.sh`, and uses `/app/run.sh` as entrypoint.

State and persistence: image layers contain disk images, kernel configs, syzkaller binaries, and sys metadata. Runtime workdir/persistent volumes are provided by Kubernetes manifests.

Dependencies and integration points: integrates with `Makefile` container target, GCS-hosted disk images, raw GitHub kernel configs, and `run.sh`.

Risks: remote `ADD` URLs make builds dependent on network and upstream content availability. Privileged runtime expectations are externalized to Kubernetes.

Test signals: Docker build success and later Kubernetes deployment behavior.
