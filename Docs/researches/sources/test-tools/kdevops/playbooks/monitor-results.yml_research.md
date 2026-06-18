# sources/test-tools/kdevops/playbooks/monitor-results.yml

Purpose: collects monitoring results from baseline/dev hosts without stopping monitoring.

Important APIs/types/functions: targets `baseline:dev` with `become: true`, optionally includes extra vars, and includes role `monitoring` tasks via `ansible.builtin.include_role` when `enable_monitoring` is true. Tags include `monitoring` and `monitor_collect`.

Control flow: load optional variables, then run monitoring collection role logic only when monitoring is enabled.

State/persistence behavior: fetches or writes monitoring result artifacts while leaving monitor processes running.

Dependencies/integration: used for mid-run collection or workflows that separate collection from process lifetime management.

Risks/test signals: collecting without stopping can race with writers and capture partial files. Test signals are generated/fetched monitoring artifacts and monitors still running afterward if expected.
