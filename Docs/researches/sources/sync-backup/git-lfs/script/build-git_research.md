# sources/sync-backup/git-lfs/script/build-git

Purpose: CI helper that installs build dependencies, builds Git from a provided source directory, installs it, and prints version/library diagnostics.

Important commands/functions: OS dispatch on `uname`, Ubuntu deb-src enablement, `apt-get build-dep git`, Homebrew curl prefix discovery, `config.mak` generation, optional curl macro patch, `make -j4`, `sudo make install`, `git --version --build-options`, `otool`, and `ldd`.

Control flow: receives the Git source directory as `$1`, performs platform-specific dependency setup, changes into that directory, conditionally patches old Git `http.h` curl compatibility macros, writes build flags disabling gettext/OpenSSL and setting prefix, builds, installs, and prints diagnostics for HTTP transport linkage.

State/persistence behavior: mutates package source lists on Linux, writes `config.mak`, may patch Git source in place, installs into `GIT_INSTALL_DIR` or `/usr/local`, and uses sudo for dependencies/install.

Dependencies/integration: used by CI jobs that need a freshly built Git binary compatible with Git LFS tests.

Risks: modifies system apt source configuration and requires sudo/network access. The patch is heuristic and may fail if Git source context changes.

Test signals: successful build, installed `git --version`, and expected curl-linked binary dependencies.
