# sources/user-network-fs/libsmb2/.github/workflows/esp_upload_component.yml

Purpose: This workflow publishes libsmb2 to the Espressif Component Service when changes land on `master`.

Important APIs and types: It uses `actions/checkout@main` and `espressif/upload-components-ci-action@v1` with component name `libsmb2`, namespace `sahlberg`, and secret `ESP_IDF_COMPONENT_API_TOKEN`.

Control flow: On a master push, one Ubuntu job checks out the repository and invokes the upload action. There is no build or validation step in this workflow itself.

State and persistence behavior: The only persistent effect is publishing a component version to Espressif's service. The API token is read from GitHub secrets and should not appear in logs.

Dependencies and integration points: It depends on Espressif component metadata in the repository, especially `idf_component.yml`, `component.mk`, and ESP-related include/source layout configured by `CMakeLists.txt`.

Risks: `actions/checkout@main` is not pinned to a version tag, and upload is triggered directly from master without an explicit ESP-IDF build gate in this workflow. Incorrect component metadata or a stale secret will fail publication after merge.

Test signals: Successful upload confirms the repository is accepted by the Espressif service. Build compatibility must be inferred from separate ESP/platform CI, not from this file.
