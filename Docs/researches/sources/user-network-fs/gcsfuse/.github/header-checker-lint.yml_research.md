## sources/user-network-fs/gcsfuse/.github/header-checker-lint.yml

Purpose: Configures license-header linting for source files.

Important APIs/types/functions: allows copyright holder `Google LLC` and license `Apache-2.0`; checks extensions/types including Go, Makefile, yml, txt, py, Dockerfile, sh, and cfg; ignores selected testdata/generated/mock files, JSON, `.github/**`, YAML, and requirements files.

Control flow: declarative config consumed by the license-header-lint app/presubmit.

State and persistence: no runtime state. Failures surface as GitHub checks or presubmit results.

Dependencies and integration points: references googleapis repo automation header-checker-lint and GitHub app installation.

Risks: `.github/**` and `*.yaml` are ignored even though workflow/config files may still need consistent licensing by policy. Extension matching for `Dockerfile`/`Makefile` depends on the lint tool's interpretation.

Test signals: presubmit check success/failure after adding or editing source files.
