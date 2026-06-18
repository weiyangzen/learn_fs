<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/swift_build_support/headeroverlay.yaml -->
# Research: sources/storage-engines/foundationdb/swift_build_support/headeroverlay.yaml

## Purpose
YAML template for Swift build support header overlay configuration.

## Important APIs, Types, And Functions
Defines `use-external-names: false`, `version: 0`, and a `roots` array populated by `@VFS_ROOTS@`.

## Control Flow
A build step substitutes virtual filesystem roots into this YAML for Swift tooling.

## State And Persistence Behavior
No runtime state; generated overlay files influence compiler header lookup.

## Dependencies And Integration Points
Depends on the Swift/CMake build support that supplies `@VFS_ROOTS@`. Integrates C/C++ headers with Swift compiler virtual filesystem overlays.

## Risks And Edge Cases
Malformed root substitution will break Swift compilation. The template is intentionally minimal, so schema drift in Swift tooling must be tracked elsewhere.

## Test Signals
Validated by Swift build configuration and compilation paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/swift_build_support/headeroverlay.yaml -->
