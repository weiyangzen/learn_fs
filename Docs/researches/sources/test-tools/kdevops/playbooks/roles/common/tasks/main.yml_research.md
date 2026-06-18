<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/common/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/common/tasks/main.yml

Source read: complete file, 89 lines, 2432 bytes, sha256 `22ce1ed2005382cb`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/common/tasks/main.yml_research.md`.

Purpose: common role tasks for optional kdevops checkout reset and user/group inference.

Important APIs/types/functions: optional `include_vars`, `ansible.builtin.git`, `command whoami`, `set_fact`, and `ansible.builtin.getent` for passwd/group lookups.

Control flow: load extra vars; optionally clone/update kdevops with retries when `kdevops_git_reset`; when `infer_uid_and_group`, capture current username, set `target_user`, query passwd and group databases, derive primary gid if no group by username exists, then set `data_user` and `data_group` either from named group or primary gid group.

State and persistence behavior: may update `kdevops_data` checkout. Mostly sets Ansible facts used by partition/filesystem roles for ownership.

Dependencies and integration: used by `create_data_partition` and any role needing correct target ownership. Depends on POSIX `whoami` and getent databases.

Risks: `GIT_SSL_NO_VERIFY=true` weakens clone verification. The group extraction expression for `getent_on_group.values()` is complex and may be brittle across Ansible versions. UID inference is skipped entirely unless `infer_uid_and_group` is defined true.

Test signals: run on hosts where username group exists and where it does not; verify `data_user`/`data_group` facts match expected ownership before creating `/data`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/common/tasks/main.yml -->
