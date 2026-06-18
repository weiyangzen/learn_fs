<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/check-apt-mirrors.yml -->
# sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/check-apt-mirrors.yml

Source read: complete file, 214 lines, 7690 bytes, sha256 `60ecba12e52952fc`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/check-apt-mirrors.yml_research.md`.

Purpose: detect and repair Debian testing APT mirror configuration, preferring a local hop1 mirror when available and falling back to official DEB822 sources when the current mirror is unreachable.

Important APIs/types/functions: delegated localhost shell calls to `scripts/get-distro-has-hop-count-sources.sh`, grep/awk parsing of DEB822 and legacy sources, `set_fact`, `stat`, `wait_for` port 80 checks, `copy` backups, `template` for `debian-hop1-mirror.sources` and `debian-testing-fallback.sources`, `file` removal of legacy sources.list, `apt update_cache`, and debug messages.

Control flow: detect hop1 mirror on control host; parse host/path; inspect target DEB822 vs legacy apt sources; parse current mirror host; check current mirror connectivity; if hop1 is available and reachable, back up sources, template hop1 DEB822 sources, remove legacy list if migrating, update apt; if current mirror failed and no reachable hop1 path is active, back up sources and install official fallback DEB822 sources.

State and persistence behavior: may rewrite `/etc/apt/sources.list.d/debian.sources`, remove `/etc/apt/sources.list`, create `.backup` files, and refresh apt cache.

Dependencies and integration: tied to Debian testing/trixie comments, devconfig mirror maintenance, templates in the role, and control-host mirror discovery script.

Risks: comments say only Debian testing, but this file has no explicit distribution/version guard internally. Registered variables for skipped tasks can be undefined; some `when` expressions assume `.stdout` fields. Migrating to DEB822 removes legacy sources, which is persistent and can surprise users.

Test signals: scenarios for DEB822 current mirror reachable, legacy current mirror reachable, current mirror unreachable with reachable hop1, unreachable hop1 fallback, missing source files, and non-Debian guarded caller behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/tasks/check-apt-mirrors.yml -->
