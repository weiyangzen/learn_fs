# sources/user-network-fs/gcsfuse/tools/package_gcsfuse/package.go

Purpose: wraps `fpm` to create deb and rpm packages from a prepared filesystem tree.

Important APIs/types/functions: `packageFpm`, `packageDeb`, and `packageRpm`.

Control flow: constructs an `fpm -s dir` command with package type, name, version, dependency on `fuse`, maintainer, URL, and description; runs it in the output directory; package-specific functions only choose `deb` or `rpm`.

State/persistence behavior: writes package files through the external `fpm` process into the output directory.

Dependencies/integration: called by package CLI after `build`; requires Ruby fpm installed.

Risks/test signals: function parameters `osys` and `arch` are unused. Package metadata is static and minimal.
