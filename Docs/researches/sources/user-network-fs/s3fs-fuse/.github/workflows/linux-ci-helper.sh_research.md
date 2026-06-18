<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/.github/workflows/linux-ci-helper.sh -->
# sources/user-network-fs/s3fs-fuse/.github/workflows/linux-ci-helper.sh

Purpose: OS-specific CI helper that installs packages inside Linux matrix containers and exports compiler/configure environment for later workflow steps.

Important APIs and variables: Accepts exactly one container name like `ubuntu:24.04` or `fedora:44`. Sets defaults `CXX=g++`, `CXXFLAGS=-O`, `LDFLAGS=`, and `CONFIGURE_OPTIONS="--prefix=/usr --with-openssl"`. Defines package manager commands, install options, package arrays, optional repository options, optional `--allowerasing`, and `CURL_DIRECT_INSTALL`. Direct curl install uses a pinned static-curl URL and architecture-specific SHA256.

Control flow: The script parses OS name/version, selects an exact branch for supported containers, updates package metadata, installs packages, prints Java version, optionally downloads/verifies/replaces `/usr/local/bin/curl` for older distributions, prints curl version, then appends environment variables to `$GITHUB_ENV`.

State and persistence: Mutates the running container by installing packages and possibly installing `/usr/local/bin/curl` plus a certificate symlink. Persists build variables only through GitHub Actions' environment file.

Dependencies and integration points: Called by `ci.yml` Linux and MemoryTest jobs. Depends on distro package managers (`apt-get`, `dnf`, `zypper`, `apk`), shell array behavior through bash-compatible execution, Java packages for tests, FUSE3 development headers, libcurl/OpenSSL/libxml2, and autotools.

Risks: The header comment says it runs in `sh`, but the shebang is bash and it uses arrays; Alpine pre-installs bash before running it. The argument-count error logs but does not immediately exit, though nounset may later fail. Package names for future distro releases can drift. Direct curl replacement is supply-chain sensitive but mitigated with SHA256 checks. `$GITHUB_ENV` must be set by GitHub Actions; local invocation without it will fail at the final append.

Test signals: Run the helper in every matrix container, verify package install success, `curl --version`, Java availability, and exported `CONFIGURE_OPTIONS`. ShellCheck is run by CI and should cover quoting/branch issues.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/.github/workflows/linux-ci-helper.sh -->
