# sources/security-integrity/ima-evm-utils/Makefile.am

## Purpose
Top-level Automake file for ima-evm-utils. It coordinates subdirectories, documentation distribution, tarball/RPM targets, manpage generation, and shellcheck delegation.

## Important APIs, Types, And Functions
- `SUBDIRS = src tests` plus optional `doc` when `HAVE_PANDOC` is true.
- `doc_DATA` distributes key-generation example scripts.
- `$(tarname)`, `tar`, and `rpm` package release artifacts.
- `evmctl.1.html`, `evmctl.1`, `rmman`, and `doc` build documentation when docbook XSL is available.
- `shellcheck` delegates to `tests`.

## Control Flow
Automake expands conditionals from `configure.ac`, then recursive make builds source, tests, and optional docs. Release targets use `git archive` tagged by package version and rpmbuild.

## State And Persistence
Generated artifacts include tarballs, manpages, HTML, temporary XSL, RPM build outputs, and cleaned `CLEANFILES`.

## Dependencies And Integration Points
Depends on Autotools variables, pandoc/asciidoc/xsltproc/docbook availability, Git tags, and RPM build tree layout.

## Risks And Edge Cases
Release packaging assumes tag `v$(PACKAGE_VERSION)` and `$HOME/rpmbuild/SOURCES`. Missing docbook XSL disables manpage distribution.

## Test Signals
Signals are successful recursive make, generated docs when enabled, and functioning `make shellcheck`, `make tar`, or `make rpm` targets.
