# sources/user-network-fs/davfs2/.github/workflows/makefile.yml

## Purpose
This GitHub Actions workflow is the davfs2 CI build definition for pushes and pull requests targeting `main`.

## Important APIs and jobs
It defines one `build` job on `ubuntu-latest`. Steps check out the repository with `actions/checkout@v4`, run `.github/workflows/setup-ubuntu.sh`, configure with `meson setup build`, compile with `ninja -C build`, and run `meson dist -C build --allow-dirty`.

## Control flow
The workflow is linear: dependency installation, Meson configuration, Ninja build, and Meson distcheck. Any failing command fails the job.

## State and persistence behavior
No project state is persisted outside the transient GitHub runner workspace. Dependency state comes from the runner apt environment.

## Dependencies and integration points
It integrates with GitHub Actions, Meson, Ninja, po4a, libneon development headers, and the repository's Meson build files. Dist generation also validates install/dist metadata.

## Risks
`ubuntu-latest` can change underneath the project, altering compiler, Meson, and libneon versions. There is no dependency cache, matrix, sanitizer, or test step beyond build/dist. The workflow name says "Makefile CI" even though it uses Meson/Ninja.

## Test signals
CI success should prove Meson configure/build and dist packaging. Improvements should test multiple Ubuntu versions or compiler modes, and include a minimal runtime or unit test target if available.
