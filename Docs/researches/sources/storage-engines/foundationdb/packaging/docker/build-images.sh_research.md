# sources/storage-engines/foundationdb/packaging/docker/build-images.sh

Purpose: This Bash helper builds and optionally pushes the FoundationDB Docker image set from local or Artifactory-provided build artifacts. It is tailored to the FoundationDB team's development environment and exits by default outside that context.

Important functions: `create_fake_website_directory` prepares a local `website` tree containing release-like binaries and client libraries from stripped/unstripped Artifactory or local build outputs. `compile_ycsb` clones or syncs YCSB and builds the FoundationDB binding. `build_and_push_images` loops over image targets, constructs tags, runs `docker build` with labels and build args, and pushes selected images.

Control flow: The script sets strict mode, logs start, derives build output/source/version/commit metadata, defines image lists, and branches on `OKTETO_NAMESPACE`. In Okteto/AWS it discovers region/account, selects build output, builds regular and debug images, and pushes them; otherwise it prints a warning and exits 1.

State and persistence behavior: It creates and deletes `packaging/docker/website`, creates `YCSB`, builds Docker images/tags, and may push to ECR or Docker registries. It does not commit anything to source control.

Dependencies and integration points: It depends on Docker, curl, tar, rsync, git, Maven, AWS metadata/CLI in Okteto, CMakeCache metadata, local build outputs, Artifactory, and the adjacent Dockerfile.

Risks: The script contains a typo `source_code_diretory`, but uses that variable consistently. Defaults are intentionally not portable. Tests should use shellcheck, dry-run builds with fake website artifacts, Okteto/ECR integration checks, and verification that debug/regular images receive correct tags and labels.
