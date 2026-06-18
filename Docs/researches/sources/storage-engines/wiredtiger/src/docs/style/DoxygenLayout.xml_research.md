# sources/storage-engines/wiredtiger/src/docs/style/DoxygenLayout.xml

## Purpose
Base Doxygen layout definition for WiredTiger documentation output.

## Structure and integration
The XML is parallel to `DoxygenLayout.11.xml` but uses a `modules` nav tab and hides the top-level classes tab. It defines the same page families: class, namespace, file, group, and directory. It exposes file lists and globals, user tabs for Community and License, and standard Doxygen sections for member declarations and definitions.

## State, dependencies, risks, tests
It is a declarative Doxygen input with no persistent state. It depends on Doxygen layout syntax and config variables such as `$SHOW_INCLUDE_FILES` and `$GROUP_GRAPHS`. Risks are mismatched behavior across Doxygen versions, hidden classes navigation surprising users, and maintaining two nearly identical layout files. Test signals are Doxygen builds across supported versions and visual checks for nav availability, file/source links, examples, modules, community, and license pages.
