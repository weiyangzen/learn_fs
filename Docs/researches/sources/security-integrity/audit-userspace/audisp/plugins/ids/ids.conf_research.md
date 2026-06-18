## sources/security-integrity/audit-userspace/audisp/plugins/ids/ids.conf

Purpose: default IDS policy configuration.

It sets thresholds/reactions for failed logins by origin, session badness, service login/root login permissions and weights, bad login weight, and reaction durations for block-address and lock-account actions. State is read by IDS config parser outside this subset and drives model/reaction behavior. Risks include aggressive defaults if enabled without tuning, duration parsing dependency, and policy semantics split across config/model/reaction modules. Test signal is loading/dumping config and exercising events that cross thresholds.
