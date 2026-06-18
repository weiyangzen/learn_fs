# sources/test-tools/syzkaller/syz-cluster/dashboard/Dockerfile

Purpose: runtime image for syz-cluster web dashboard.

Important APIs/types/functions: multi-stage Dockerfile using common syz-cluster builder and Alpine runtime.

Control flow: copies `/build/syz-cluster/bin/web-dashboard` to `/bin/web-dashboard`, exposes 8081, and sets entrypoint.

State and persistence: image only; dashboard state comes from backend services.

Dependencies and integration points: built by syz-cluster Makefile.

Risks: assumes builder image produced the binary at the expected path.

Test signals: Docker build and dashboard pod startup.
