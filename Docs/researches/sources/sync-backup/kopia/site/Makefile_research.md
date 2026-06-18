# sources/sync-backup/kopia/site/Makefile

Purpose: defines build, serve, dependency install, cleanup, and generated CLI reference tasks for the Kopia Hugo site.

Important APIs/types/functions: targets are `all`, `install-tools`, `build`, `server`, `node_modules`, `clean`, and `gen-cli-reference-pages`. It includes `../tools/tools.mk` and uses variables such as `npm`, `cli2mdbin`, `hugo`, `TOOLS_DIR`, `npm_flags`, and `npm_install_or_ci`.

Control flow: `all` builds. `build` installs tools, generates CLI reference pages, installs node modules, then runs Hugo. `server` starts Hugo server with configurable `WATCH=false`. `node_modules` runs npm install/ci without audit then runs production audit excluding dev dependencies. Netlify production builds export `HUGO_ENV=production`.

State and persistence behavior: writes generated site output under `public/`, Hugo resources under `resources/`, node dependencies under `node_modules/`, and generated CLI reference content through `cli2md`. `clean` removes generated output, dependencies, and tool directory.

Dependencies/integration: integrates Hugo, npm, generated CLI reference tooling, Netlify environment variables, and repository-level tools.mk.

Risks: `clean` removes shared tool directory. The comment warns that putting tools under the site directory can break `make server` due to open-file pressure from `node_modules`. Audit omits dev dependencies even though all package dependencies are dev dependencies for the site build.

Test signals: build correctness is validated by running make targets externally; no test code here.
