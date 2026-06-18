# sources/sync-backup/borg/docs/global.rst.inc Research

## Purpose

`global.rst.inc` centralizes common reStructuredText substitutions and external link targets used across BorgBackup documentation. It avoids repeating package names, repository URLs, cryptography terminology links, dependency links, and related references in many `.rst` files.

## Important APIs, Types, and Functions

The file sets default highlighting to bash with `.. highlight:: bash`, defines substitutions such as `|package_dirname|`, `|package_filename|`, `|package_url|`, and `|git_url|`, and declares named hyperlink targets for GitHub, the issue tracker, deduplication, AES, HMAC-SHA256, SHA256, PBKDF2, argon2, ACL/libacl/libattr, compression libraries, OpenSSL, Python 3, Buzhash, msgpack, FUSE bindings, userspace filesystems, Cython, and virtualenv.

## Control Flow

There is no executable control flow. Sphinx/docutils processes this include wherever docs use `.. include:: global.rst.inc` or relative includes from subdirectories.

## State and Persistence Behavior

The file contributes substitutions and link definitions to document parsing. It does not generate files directly or store runtime state.

## Dependencies and Integration Points

Many docs files include this file, including top-level and internals/deployment pages with relative paths. It integrates with Sphinx substitution replacement, external link checking, and documentation terminology consistency.

## Risks and Edge Cases

Stale external URLs can create linkcheck failures or mislead readers. Because includes are relative, moving docs files can break include paths. Substitution values using `|version|` depend on Sphinx version substitution from `docs/conf.py`.

## Test Signals

Sphinx builds validate substitution definitions and include paths. `make -C docs linkcheck` is the main signal for stale external references.
