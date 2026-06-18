# sources/test-tools/strace/maint/make-dsc

Purpose: emits a Debian `.dsc` source control file for given tarball artifacts using metadata from `debian/control` and `debian/changelog`.

Important APIs/types/functions: stdin redirected from `/dev/null`, `sed` extraction of package fields, package-list construction for `strace`, `strace64`, and `strace-udeb`, and checksum sections using `sha1sum`, `sha256sum`, `md5sum`, and `stat -c %s`.

Control flow: print fixed `Format: 1.0`, derive source/binary/architecture/version/maintainer/homepage/standards/build-depends fields, print package list with arch values, then iterate input files for SHA1, SHA256, and MD5 file entries while transforming tarball names to Debian `.orig` naming.

State and persistence behavior: stdout only; reads Debian packaging files and artifact files.

Dependencies and integration points: called by `make-dist` to produce `strace.dsc` for release artifacts.

Risks: assumes exact Debian control paragraph formatting and package names. Filename transformation is simple and may not cover unusual artifact names.

Test signals: generated `.dsc` should parse with Debian tooling and contain correct checksums/sizes for all supplied tarballs.
