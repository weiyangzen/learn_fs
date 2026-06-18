# sources/distributed-fs/tahoe-lafs/misc/build_helpers/gen-package-table.py

## Purpose

This script generates an HTML dependency package table from directories containing Tahoe-LAFS dependency archives. It classifies archive filenames by package, Python version, and platform, then emits separate tables for platform-dependent and platform-independent packages.

## Important APIs, Types, and Functions

Global regexes `FILENAME_RE` and `FILENAME_RE2` parse egg/sdist/exe names. `platform_aliases` normalizes platform suffixes, and `min_supported_python` marks unsupported Windows Python versions. `add` appends values into a dict-of-lists. `file_list` sorts files using `pkg_resources.parse_version` and renders links.

## Control Flow

The script gathers filenames from `.` and `../tahoe-dep-sdists` unless arguments override the directories. For each supported extension, it parses package/version/Python/platform fields, normalizes platform names, records package membership, and populates `matrix[pythonver][platform]`. It then prints complete HTML 4.01 with one table per Python version for compiled/platform packages and one table for source or platform-independent artifacts.

## State, Dependencies, Integration, Risks, and Tests

State is in global sets and dictionaries during one run; output is stdout. Dependencies are `pkg_resources`, directory listings, and strict historical filename conventions. Integration is dependency mirror publishing. Risks include brittle regex parsing, direct HTML interpolation of filenames, assuming `matrix['']['']` exists, and old package naming assumptions. Tests should feed fixture directories with eggs, sdists, Windows installers, aliases, package-name continuations, and malformed files.
