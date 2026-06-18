# sources/user-network-fs/nfs-utils/support/include/nls.h

## Purpose
Provides gettext/no-gettext translation macros for nfs-utils command output.

## Important APIs, Types, and Functions
Defines `LOCALEDIR`, `_()`, and `N_()` depending on `ENABLE_NLS`, and stubs `bindtextdomain()`/`textdomain()` when NLS is disabled.

## Control Flow
Translatable strings are wrapped at compile time. With NLS enabled they call gettext; otherwise strings are returned unchanged.

## State and Persistence Behavior
No project state. Runtime gettext may read locale catalogs.

## Dependencies and Integration Points
Used by command-line tools that need optional localization.

## Risks and Edge Cases
Macro stubs can hide missing gettext initialization in non-NLS builds. `LOCALEDIR` fallback must match installation layout.

## Test Signals
Build with and without `ENABLE_NLS`, run output smoke tests under different locales, and verify catalog lookup paths.
