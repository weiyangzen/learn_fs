# sources/test-tools/strace/debian/changelog.in

## Purpose
Provides the Autoconf-substituted Debian changelog template for strace packaging. The top entry is generated for the current snapshot, followed by historical Debian package changelog records from recent 7.x releases back through early strace Debian packaging.

## Important APIs, Types, and Functions
Read coverage: 1244 lines and 38694 bytes. The template uses substitution tokens `@PACKAGE_VERSION@`, `@PACKAGE_STRING@`, `@PACKAGE_BUGREPORT@`, and `@DEB_CHANGELOGTIME@` in the first `experimental` entry. Historical entries record upstream versions, Debian revisions, urgency, maintainers, uploaders, bug closure references, and notable packaging/build changes. There are no functions; the file is a Debian policy-format data source consumed by configure and packaging tools.

## Control Flow
During configure, `AC_CONFIG_FILES([debian/changelog])` substitutes package metadata and the generated RFC-2822 changelog timestamp into this template. Debian packaging tools then consume the resulting `debian/changelog` to determine source package version, distribution, urgency, maintainer signature, and release history for `dh_installchangelogs`, source package construction, and archive metadata.

## State and Persistence Behavior
The generated `debian/changelog` is persistent packaging metadata in the build tree. It records release history and current snapshot identity but does not affect strace runtime behavior. The top generated stanza changes with package version and configure time, while historical records are static and source-controlled in the template.

## Dependencies and Integration Points
Depends on Autoconf substitution from `configure.ac` and Debian packaging tools that parse changelog format. It integrates with `debian/rules`, `dh_installchangelogs`, source package versioning, release snapshots, maintainer workflows, and downstream bug tracking references in historical entries.

## Risks and Edge Cases
Malformed changelog syntax can break Debian package builds. Incorrect substitution values can produce wrong package versions, maintainer contact, or timestamps. The generated top entry targets `experimental`, so release packaging must intentionally adjust if a different distribution is needed. Very old historical entries include legacy formatting and bug references; changes should avoid disturbing parseable Debian changelog structure.

## Test Signals
Run configure and verify `debian/changelog` is generated with the expected current package version, package string, bug-report address, and timestamp. Run `dpkg-parsechangelog` and a Debian package build to validate syntax, check `dh_installchangelogs` output, and confirm the top generated entry matches release expectations.
