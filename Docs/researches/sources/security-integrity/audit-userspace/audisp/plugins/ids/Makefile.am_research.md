## sources/security-integrity/audit-userspace/audisp/plugins/ids/Makefile.am

Purpose: experimental IDS plugin build/install fragment.

It builds `audisp-ids` from account, AVL, config, models, reactions, session, and timer sources, links libaudit/auparse/common/auplugin, installs plugin and IDS configs, and includes rules subdir. State is installed experimental binary/config. Dependencies are `ENABLE_EXPERIMENTAL`, auparse normalization, audit logging, and model modules not all in this subset. Risks include broad module coupling and experimental status requiring explicit CI flags. Test signal is CI with `--enable-experimental` and plugin model tests if present.
