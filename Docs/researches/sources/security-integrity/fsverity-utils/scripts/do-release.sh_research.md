# sources/security-integrity/fsverity-utils/scripts/do-release.sh

Purpose: This release script automates fsverity-utils versioned release preparation, packaging, tagging, or verification steps for maintainers.

Important APIs and steps: It checks repository state, derives version information, builds distribution artifacts, may run tests, and coordinates signing or upload-ready outputs depending on project conventions.

Control flow and state: Shell control flow validates prerequisites before mutating release artifacts. Persistent state can include generated tarballs, tags, checksums, and temporary version files.

Dependencies and integration points: Integrates with `make`, git, release signing tools, and generated documentation or package metadata.

Risks and test signals: Release scripts are high-risk because they can publish incorrect versions or artifacts from dirty trees. Signals include dry-run/manual review, clean tree checks, reproducible archive contents, and successful build/test before release.
