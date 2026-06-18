# sources/sync-backup/git-lfs/script/update-version

Purpose: release helper that updates Git LFS version declarations across Go, Debian, RPM, and Windows version metadata.

Important functions: `rfc822_datestamp`, `user_id`, `update_go`, `update_debian`, `update_rpm`, `update_versioninfo`, and `main`.

Control flow: validates `NEW-VERSION`, strips leading `v`, updates `config/version.go`, prepends a Debian changelog entry if needed, rewrites RPM `Version:`, and updates `versioninfo.json` major/minor/patch/product fields.

State/persistence behavior: writes four tracked files. Debian changelog uses a deterministic 14:29 UTC-ish timestamp and current Git committer identity.

Dependencies/integration: release process before packaging and upload; uses sed, ruby, git, date, and mktemp.

Risks: sed/ruby regexes assume simple numeric dotted versions and fixed file formats. Debian update is idempotent only by grep for `git-lfs ($version)`.

Test signals: git diff after running should show consistent version bumps and no duplicate Debian changelog entry.
