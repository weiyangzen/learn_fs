<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/.tx/config -->
# sources/security-integrity/selinux/policycoreutils/.tx/config

## Purpose

Transifex client configuration for policycoreutils translation resources. The source was read completely for this report (8 lines).

## Important APIs, Types, and Functions

Defines the Transifex project/resource mapping, source language, source file path, and translated file path pattern for localization workflows.

## Control Flow

No executable flow; external `tx` tooling reads the config to pull or push translation catalogs.

## State and Persistence Behavior

Persistent state is translation metadata in the repository plus downloaded/generated locale files when the external tool runs.

## Dependencies and Integration Points

Integrates policycoreutils with the Transifex translation service and the build system `LINGUAS` locale installation paths.

## Risks and Edge Cases

Risks include stale project/resource names, path changes that break translation sync, and accidental overwrites by external tooling.

## Test Signals

Signals are successful `tx status/pull` operations and localized man/message build output.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/.tx/config -->
