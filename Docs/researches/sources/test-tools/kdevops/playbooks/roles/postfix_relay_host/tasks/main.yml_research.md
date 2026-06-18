<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/postfix_relay_host/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/postfix_relay_host/tasks/main.yml

Purpose: configures Postfix to use a relay host when enabled.

Important APIs/types/functions: modules `ansible.builtin.include_vars`, `ansible.builtin.stat`, `ansible.builtin.lineinfile`, `ansible.builtin.systemd`; variables/facts `ignore_errors`, `with_first_found`, `skip`, `become_flags`, `become_method`, `regexp`, `line`, `enabled`, `masked`; tasks `Import optional extra_args file`, `Check to see if /etc/postfix/main.cf exists`, `Set relayhost on /etc/postfix/main.cf`, `Enable and restart postfix service`.

Control flow: Loads optional extra vars, stats `/etc/postfix/main.cf`, replaces or adds the `relayhost` setting with `lineinfile`, then enables and restarts postfix.

State and persistence behavior: Mutates `/etc/postfix/main.cf` and postfix systemd service state.

Dependencies and integration points: Depends on postfix being installed and `postfix_relay_host_setup`/`postfix_relay_host` variables.

Risks: If Postfix is absent the role silently skips after stat. Bad relayhost values are not validated before restart.

Test signals: Signals are changed relayhost line, active postfix service, and successful mail relay test.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/postfix_relay_host/tasks/main.yml -->
