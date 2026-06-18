# sources/test-tools/syzkaller/syz-cluster/controller/Dockerfile

Purpose: runtime image for syz-cluster controller.

Important APIs/types/functions: multi-stage Dockerfile using `${IMAGE_PREFIX}syz-cluster-build:${IMAGE_TAG}` as builder and Alpine runtime.

Control flow: copies `/build/syz-cluster/bin/controller` into `/bin/controller`, exposes 8080, and sets entrypoint.

State and persistence: image only; runtime state is external databases/blob storage.

Dependencies and integration points: built by syz-cluster Makefile component macro.

Risks: assumes common builder image already contains compiled controller binary.

Test signals: Docker build and pod startup.
