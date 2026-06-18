# sources/storage-engines/foundationdb/documentation/sphinx/source/guide-common.rst.inc

## Purpose
Shared RST substitutions for FoundationDB installation and administration guides. It covers platform warnings, cluster-file rules, development-mode defaults, upgrades, server process configuration, coordinator selection, config-file updates, and package filenames.

## Important APIs, Types, and Functions
Defines substitutions including `|platform-not-supported-for-production|`, `|cluster-file-rule1|` through `|cluster-file-rule3|`, `|simple-installation-mode-warnings|`, `|networking-clarification|`, `|development-use-only-warning|`, `|upgrade-client-server-warning|`, `|optimize-configuration|`, `|coordinators-auto|`, `|conf-file-change-detection|`, and package filename substitutions for deb, rpm, macOS, and Windows.

## Control Flow
Consuming pages include the file and reference substitutions. Sphinx expands them at build time, using broader substitutions such as `|release|`.

## State and Persistence Behavior
Static documentation state only. Package substitutions encode release-sensitive artifact naming through `|release|`.

## Dependencies and Integration Points
Depends on Sphinx substitutions and references to installation/configuration/system-requirements pages. Integrates with release packaging conventions and platform-specific guide pages.

## Risks
Production-support statements, package names, memory guidance, and coordinator recommendations can drift from current release policy. Misuse on the wrong platform page can mislead users.

## Test Signals
Full Sphinx build with warnings as errors; release validation comparing rendered package names to artifacts; documentation review against current support and configuration guidance.
