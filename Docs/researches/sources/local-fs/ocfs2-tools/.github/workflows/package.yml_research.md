# File Research: sources/local-fs/ocfs2-tools/.github/workflows/package.yml

## Role

This GitHub Actions workflow is a minimal packaging smoke job for `ocfs2-tools`.

## Behavior

It runs on pushes and pull requests targeting `master`, checks out the repository on `ubuntu-latest`, and creates `ocfs2-tools.tar.gz` with `tar -cvf ocfs2-tools.tar.gz *`.

## Dependencies And Risks

The workflow does not build, test, install dependencies, or upload the generated tarball as an artifact. The archive command excludes dotfiles such as `.github` because it uses `*`, and the file extension says `.gz` even though `tar -cvf` does not gzip.
