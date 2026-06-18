# sources/user-network-fs/fusepy/MANIFEST.in

## Purpose
`MANIFEST.in` controls source distribution inclusion for fusepy. It includes README files in package archives.

## Important APIs, Types, and Functions
No runtime APIs are defined. The only packaging directive is `include README*`.

## Control Flow
During Python packaging source distribution creation, setuptools/distutils reads this manifest and includes files matching `README*`.

## State and Persistence
No runtime state. It affects persisted release artifacts by ensuring README documentation is packaged.

## Dependencies and Integration Points
It integrates with Python packaging tools that honor `MANIFEST.in`.

## Risks and Edge Cases
The manifest is minimal; licenses, examples, tests, or other metadata are not included by this directive unless included elsewhere by setup configuration. README glob behavior depends on packaging tool conventions.

## Test Signals
Build an sdist and inspect its file list to confirm expected README files are included and no required ancillary files are omitted.
