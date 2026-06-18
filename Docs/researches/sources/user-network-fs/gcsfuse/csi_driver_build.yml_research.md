<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/csi_driver_build.yml -->
# Research: sources/user-network-fs/gcsfuse/csi_driver_build.yml

Purpose: Google Cloud Build pipeline for building gcsfuse binaries and embedding them into a GCS Fuse CSI Driver image.

Important data/APIs: substitutions define Go version, gcsfuse version, CSI driver branch, ARM build toggle, image owner/prefix, and optional staging version. Steps clone `GoogleCloudPlatform/gcs-fuse-csi-driver`, run `tools/build_gcsfuse/main.go`, create a temporary GCS bucket, upload linux architecture artifacts, build/push the CSI driver image with `make build-image-and-push-multi-arch`, and remove the temporary bucket.

Control flow: clone, build, and bucket creation start concurrently. Binary upload waits for build and bucket creation; image build waits for upload and clone; cleanup waits for image build.

State and persistence: persistent outputs are pushed container images and uploaded artifacts consumed during the same build. Temporary state includes `/workspace/gcsfuse-artifacts`, `/workspace/bucket_name`, `csi-driver-src`, and a short-lived GCS bucket.

Dependencies: Cloud Build, git, golang image, gcloud storage, docker builder, apt package installation inside the docker step, GCR auth, CSI driver Makefile targets, and project IAM permissions for bucket/image operations.

Risks: cleanup runs only after successful image build, so failed builds may leave temporary buckets. The docker step installs cloud SDK dynamically, increasing network/time fragility. Branch/version substitutions control supply-chain inputs and should be pinned for release builds.

Test signals: dry-run Cloud Build with `_BUILD_ARM=false` and true, verify artifacts under both linux arches, image tags, bucket cleanup, and CSI driver image can find the staged gcsfuse binaries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/csi_driver_build.yml -->
