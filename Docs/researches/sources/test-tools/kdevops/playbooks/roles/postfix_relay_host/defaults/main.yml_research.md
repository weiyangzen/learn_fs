<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/postfix_relay_host/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/postfix_relay_host/defaults/main.yml

Purpose: defines whether postfix relay-host setup is enabled and the relay host value to write into Postfix configuration.

Important APIs/types/functions: variables/facts `postfix_relay_host_setup`, `postfix_relay_host`.

Control flow: Defaults are consumed by the relay-host task file.

State and persistence behavior: No direct state; variables gate later config mutation.

Dependencies and integration points: Used by host setup that wants outbound mail routed through a relay.

Risks: Incorrect relayhost breaks mail delivery; disabling setup leaves existing config untouched.

Test signals: Signals are expected default variable values and rendered `relayhost` line when enabled.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/postfix_relay_host/defaults/main.yml -->
