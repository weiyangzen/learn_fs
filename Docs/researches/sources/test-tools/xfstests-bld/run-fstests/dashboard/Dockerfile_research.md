# sources/test-tools/xfstests-bld/run-fstests/dashboard/Dockerfile

Purpose: container image definition for the GCE xfstests dashboard Flask app, suitable for Cloud Run-style deployment.

Important steps: base image `google/cloud-sdk`, sets `PYTHONUNBUFFERED`, copies app code to `/app`, installs Python packages `Flask`, `gunicorn`, `junit-xml`, and `junitparser`, then runs gunicorn bound to `$PORT`.

Control flow/state: image build bakes source into `/app`; runtime starts one gunicorn worker with eight threads and no timeout.

Dependencies/integration: needs Google Cloud SDK for `gcloud storage rsync`, Python/pip, dashboard.py, and environment variables consumed by the app.

Risks: unpinned pip dependencies can change behavior. `MAINTAINER` is deprecated. Running from a broad cloud-sdk base increases image size. One worker may limit CPU utilization.

Test signals: container should start with a dummy `$PORT`, import `dashboard:app`, and successfully execute `/sync` when credentials and `RESULTS_GS_PATH` are configured.
