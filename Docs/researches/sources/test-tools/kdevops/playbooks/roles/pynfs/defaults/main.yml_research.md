<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/pynfs/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/pynfs/defaults/main.yml

Purpose: sets pynfs source repository, tag, data path, and pNFS block test enablement defaults.

Important APIs/types/functions: variables/facts `kdevops_run_pynfs`, `pynfs_pnfs_block`, `pynfs_data`.

Control flow: Variables are consumed by clone/build/export/run tasks in the pynfs role.

State and persistence behavior: No direct state; values control source checkout and result behavior.

Dependencies and integration points: Integrated with nfsd_add_export and workflow scripts `run_pynfs.sh` and `run_pynfs_block.sh`.

Risks: Repo/tag drift affects reproducibility; enabling pNFS requires matching server/export support.

Test signals: Signals are checkout at expected tag and expected result files for v4.0/v4.1/block.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/pynfs/defaults/main.yml -->
