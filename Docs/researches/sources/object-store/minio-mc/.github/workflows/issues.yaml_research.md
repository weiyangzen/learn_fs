<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/.github/workflows/issues.yaml -->
# sources/object-store/minio-mc/.github/workflows/issues.yaml

## Purpose
GitHub Actions workflow that adds newly opened issues to a MinIO organization project.

## Important APIs, types, and functions
On `issues: opened`, it runs `actions/add-to-project@v0.5.0` with the configured project URL and `secrets.BOT_PAT`.

## Control flow
Each new issue triggers one Ubuntu job and one project-add step.

## State and persistence behavior
No code state. It mutates GitHub Projects membership for issues.

## Dependencies and integration points
Depends on a valid BOT_PAT secret and access to `https://github.com/orgs/miniohq/projects/2`.

## Risks and test signals
Expired or under-scoped tokens leave issues untracked. Test signal is successful workflow run and issue appearing in the project.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/.github/workflows/issues.yaml -->
