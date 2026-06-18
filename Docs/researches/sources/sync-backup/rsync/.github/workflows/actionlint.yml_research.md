# sources/sync-backup/rsync/.github/workflows/actionlint.yml

Purpose: lint GitHub Actions workflow YAML.

Important APIs/types/functions: workflow triggers on pushes and pull requests to `master` when workflow/actionlint config files change; job installs pinned `rhysd/actionlint` version `1.7.12`, prints version, and runs `actionlint -color`.

Control flow: single `ubuntu-latest` job with read-only contents permission.

State and persistence: no artifacts; only CI logs.

Dependencies/integration: depends on `actions/checkout@v4`, curl over TLS, and actionlint's embedded checks including shellcheck-like validation.

Risks: download script is remote but version-pinned. Path filters mean workflow issues outside changed workflow files are caught only when those paths trigger.

Test signals: CI status is the signal; catches malformed YAML, expressions, runner references, and many shell mistakes.
