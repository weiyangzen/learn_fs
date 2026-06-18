# sources/sync-backup/casync/src/def.h

## Purpose

`def.h` centralizes small global constants for casync's source tree: node limits, buffer size, and supported feature masks based on build-time SELinux support.

## Important APIs, Types, and Functions

`NODES_MAX` is `64`. `BUFFER_SIZE` is `64U*1024U`. `SUPPORTED_FEATURE_MASK` is either `CA_FORMAT_FEATURE_FLAGS_MAX` when `HAVE_SELINUX` is true or that mask with `CA_FORMAT_WITH_SELINUX` removed. `SUPPORTED_WITH_MASK` intersects `CA_FORMAT_WITH_MASK` with the supported feature mask.

## Control Flow

There is no runtime control flow. Preprocessor branches select feature support at compile time.

## State and Persistence Behavior

The header stores no state. Its macros affect runtime behavior in files like `casync.c` by controlling default encode features and accepted decode feature masks.

## Dependencies and Integration Points

It depends on format feature macros being visible before or through users that include it. `casync.c` uses it for default encode feature flags and buffer sizes. `copy.c` uses `BUFFER_SIZE` through its include chain.

## Risks and Edge Cases

Build configurations without SELinux intentionally reject or mask SELinux metadata support. If format constants change, this header must stay aligned. Broad macros in a small global header can silently affect many call sites.

## Test Signals

Build tests should compare feature masks with and without `HAVE_SELINUX`, and runtime archive compatibility tests should verify SELinux metadata is included only when supported.
