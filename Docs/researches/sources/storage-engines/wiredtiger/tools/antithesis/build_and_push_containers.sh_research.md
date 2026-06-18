# sources/storage-engines/wiredtiger/tools/antithesis/build_and_push_containers.sh

## Purpose
This shell script builds and pushes Antithesis Docker images for WiredTiger `test/format` workloads. It is intended for CI environments with task metadata and registry credentials in environment variables.

## Important commands and variables
Key variables are `task_name`, `is_patch`, `antithesis_image_tag`, `branch_name`, `build_id`, `revision`, and `antithesis_repo_key`. The script writes `../../cmake_build/VERSION`, builds `wt-test-format:$tag` from `test_format.dockerfile`, rewrites `docker-compose.yaml` from `wt-latest` to the tag, builds `wt-test-format-config:$tag` from `config.docker`, logs in to `us-central1-docker.pkg.dev`, tags both images into the MongoDB repository path, pushes them, and logs out.

## Control flow and behavior
With `errexit` and verbose shell mode, any failing command aborts. The tag defaults to `${task_name}-latest`, changes to `${task_name}-patch` for patch builds, and is overridden by `antithesis_image_tag` when present. Registry credentials are written temporarily to `mongodb.key.json`, piped to `docker login`, then removed.

## State, dependencies, and integration
The script mutates the local compose file via `sed -i`, writes a version file in the build directory, creates local Docker images, and pushes remote registry tags. It depends on `sudo docker`, the Antithesis Dockerfiles, `docker-compose.yaml`, CI metadata, and Google Artifact Registry credentials.

## Risks and test signals
Risks include in-place compose-file mutation, credentials touching disk, reliance on `sudo`, unquoted environment expansion in some paths, and stale tags if CI variables are absent. Signals include successful image builds, registry login/push output, expected image tags in Artifact Registry, and a version file containing branch/build/revision metadata.
