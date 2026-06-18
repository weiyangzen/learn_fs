# File Research: sources/virtualization/guestfs-tools/.github/workflows/main.yml

## Scope

GitHub Actions CI for `guestfs-tools`, triggered on pushes to `master`, `ci/**`, pull requests to `master`, and manual dispatch.

## Behavior

- The active job is Fedora 43 running inside a privileged `quay.io/fedora/fedora` container on `ubuntu-latest`.
- Installs build dependencies with `dnf builddep guestfs-tools libguestfs`, adds `git`, `kernel`, and `sqlite`, and removes OCaml libguestfs packages to avoid multiple-definition warnings.
- Checks out `guestfs-tools`, clones and builds current `libguestfs`, then configures/builds `guestfs-tools` through `./libguestfs/run`.
- Runs `make check`, printing any `test-suite.log` files on failure.
- Contains a fully commented Ubuntu job showing a similar source-package build-dependency path.

## Dependencies And Risks

- Requires Fedora builddep metadata and network access to clone libguestfs.
- Privileged container is needed for libguestfs-style appliance/KVM tests.
- Tracks latest libguestfs `master` by shallow clone, so CI may fail from upstream incompatibilities not pinned to a commit.
