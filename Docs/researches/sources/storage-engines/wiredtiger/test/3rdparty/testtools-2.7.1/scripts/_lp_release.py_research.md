# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/scripts/_lp_release.py

Purpose: Launchpad release automation script for testtools.

Important APIs, types, and functions: constants define app name, cache directory, Launchpad service root, bug statuses, tarball file type, project name, and `next` milestone. `_UTC` supplies timezone handling. Functions configure logging, resolve repo paths, assign fix-committed bugs to `next`, rename/release/create milestones, parse NEWS release notes/changelog, upload tarballs and signatures, close fixed bugs, and run `release_project()` from `main()`.

Control flow: `main()` logs into Launchpad using `.lp_creds`, gets the project and `next` milestone, parses the next release from `NEWS`, validates tarball/signature and milestone absence, reassigns bugs, renames `next` to the release, creates the product release, uploads the tarball, creates a new `next`, and marks milestone tasks released or unassigns non-fixed tasks.

State and persistence: mutates remote Launchpad bugs, milestones, releases, and uploaded files. Locally reads `NEWS`, `dist/<project>-<version>.tar.gz`, signature, and credential/cache files.

Dependencies and integration points: depends on `launchpadlib`, `Makefile release`, Launchpad project conventions, and NEWS heading formatting.

Risks and test signals: operations are hard to reverse and validation is limited to a few preflight checks. `upload_tarball()` opens tarball/signature in text mode, which may be risky for binary content under Python 3. Test signals are dry-run/preflight failures for missing artifacts and controlled release execution against Launchpad.
