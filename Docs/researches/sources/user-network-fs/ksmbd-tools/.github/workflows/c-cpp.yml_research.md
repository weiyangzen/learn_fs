# sources/user-network-fs/ksmbd-tools/.github/workflows/c-cpp.yml

Purpose: GitHub Actions workflow for ksmbd-tools CI builds across autotools and Meson, with and without Kerberos support.

Important APIs, types, and functions: Workflow `ksmbd-tools CI` triggers on pushes and pull requests to `master` and `next`; one `build` job runs on `ubuntu-latest`; steps use `actions/checkout@v4`, apt package installation, `pip3 install --user meson`, `./autogen.sh`, `configure`, `make distcheck`, and `meson dist`.

Control flow: Installs build prerequisites, prints compiler versions, bootstraps autotools, then runs six build/dist lanes: autotools without krb5, autotools with MIT krb5, autotools with Heimdal krb5, Meson without krb5, Meson with MIT krb5, and Meson with Heimdal krb5.

State and persistence behavior: Creates temporary build directories inside the CI workspace. No artifacts are explicitly uploaded.

Dependencies and integration points: Integrates Ubuntu packages for netlink, GLib, MIT/Heimdal Kerberos, Ninja, Meson, autotools, and ksmbd-tools packaging checks.

Risks: `PATH=$HOME/.local/bin:$PATH` is scoped only within that shell step, but all Meson invocations occur in later steps where GitHub may not preserve the assignment. Package names and distro versions can change on `ubuntu-latest`.

Test signals: Strong build/distribution signal across both supported build systems and Kerberos provider variants, but no runtime tests are shown.
