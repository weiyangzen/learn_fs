# sources/test-tools/syzkaller/syz-agent/lore-relay/Dockerfile

Purpose: builds the syz-lore-relay container image.

Important APIs/types/functions: multi-stage Dockerfile using `gcr.io/syzkaller/env` builder and `alpine:latest` runtime.

Control flow: downloads Go modules, copies source, runs `CGO_ENABLED=0 make lore-relay`, installs git/ca-certificates in Alpine runtime, copies binary, and sets entrypoint.

State and persistence: image contains only binary and runtime packages; lore repository state is mounted by Kubernetes.

Dependencies and integration points: used by syz-agent Makefile `lore-relay-container`.

Risks: runtime depends on Alpine package availability during build. Static build assumes no CGO runtime requirements.

Test signals: Docker build and container startup.
