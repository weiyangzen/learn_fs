# sources/distributed-fs/tahoe-lafs/towncrier.toml

## Purpose
This configuration defines Tahoe-LAFS release-note generation with Towncrier.

## Important APIs, Types, and Functions
It configures `package_dir = "src"`, `package = "allmydata"`, output `filename = "NEWS.rst"`, fragment `directory = "newsfragments"`, `start_string`, release `title_format`, Trac ticket `issue_format`, and underline styles. It defines fragment categories: `security`, `incompat`, `feature`, `bugfix`, `installation`, `configuration`, `documentation`, `removed`, `other`, and hidden-content `minor`.

## Control Flow
Towncrier reads this TOML file during `towncrier.check`, draft generation, or release rendering. Fragment files in category directories are grouped by the listed type order and inserted into `NEWS.rst` at the configured start marker.

## State and Persistence
The source state is the `newsfragments` directory and package metadata under `src/allmydata`. Generated release state is persisted in `NEWS.rst` when Towncrier is run in release mode.

## Dependencies and Integration Points
Integrated by `tox.ini` environments `codechecks`, `draftnews`, and `news`. The `issue_format` points to Tahoe-LAFS Trac tickets, so fragment names are expected to map to ticket ids and type suffixes.

## Risks and Test Signals
Changing directory names breaks contributor fragment validation. `minor` uses `showcontent = false`, so fragments in that type intentionally affect categorization without rendering body text. Test signals are successful `python -m towncrier.check --config towncrier.toml`, draft generation, and release generation against representative fragments.
