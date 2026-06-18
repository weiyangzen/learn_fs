# sources/sync-backup/kopia/site/package.json

Purpose: declares Node package metadata and development dependencies for the Kopia site.

Important APIs/types/functions: package name `site`, version `0.0.1`, description `"Kopia site."`, `main` set to `none.js`, license `ISC`, and dev dependencies `autoprefixer`, `postcss`, and `postcss-cli`.

Control flow: npm reads dependency ranges during install/ci; build commands are in the Makefile rather than npm scripts.

State and persistence behavior: no runtime state; this is the source of dependency intent, while `package-lock.json` pins actual versions.

Dependencies/integration: integrates with site CSS processing and the Makefile `node_modules` target.

Risks: no npm scripts means build behavior is split across Makefile and package metadata. Dependency ranges allow minor/patch updates unless lockfile is used.

Test signals: install/audit/build commands validate dependency usability.
