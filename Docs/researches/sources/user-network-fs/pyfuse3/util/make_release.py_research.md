# sources/user-network-fs/pyfuse3/util/make_release.py

Purpose: Automates mechanical pyfuse3 release preparation: parse changelog version, optionally rotate signify keys, commit/tag, build docs and sdist, sign tarball, and generate announcement text.

Important APIs/types/functions: Constants `ROOT`, `CHANGES`, `SIGNIFY_DIR`, `VERSION_HEADING_RE`, and `ANNOUNCEMENT_TEMPLATE`. Helpers `run`, `capture`, `parse_changes`, `signing_keys_dir`, `rotate_keys`, `contributor_list`, and `main`.

Control flow: `main` checks required tools, parses the top release heading from `Changes.rst`, finds previous tag, rotates keys for new major/minor revision, commits all changes, tags, runs `uv sync`, builds Sphinx docs and sdist, signs the tarball, and prints an announcement.

State and persistence: Mutates git history/tags, key files under `signify` and external signing key directory, `dist/` artifacts, built docs, and terminal output. It requires environment variable `PYFUSE_SIGNING_KEYS_DIR` when key rotation is needed.

Dependencies and integration points: Depends on git, signify, uv, Sphinx, pyfuse3 packaging, changelog format, and release key layout.

Risks: It runs `git commit --all` and `git tag`, so dirty unrelated changes could be included if used carelessly. Key rotation renames files and deletes obsolete public keys. Changelog parser accepts only specific heading formats.

Test signals: No direct tests. Safe usage is validated by release dry runs and tool failures; because of side effects, this script should not be executed by normal tests.
