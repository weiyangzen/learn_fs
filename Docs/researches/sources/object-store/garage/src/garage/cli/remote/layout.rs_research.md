# sources/object-store/garage/src/garage/cli/remote/layout.rs

Purpose: implements remote CLI cluster layout staging, preview, apply, revert, history, and dead-node progress forcing.

Important APIs/types/functions: `layout_command_dispatch`; command methods `cmd_show_layout`, `cmd_assign_role`, `cmd_remove_role`, `cmd_config_layout`, `cmd_apply_layout`, `cmd_revert_layout`, `cmd_layout_history`, `cmd_skip_dead_nodes`; helpers `capacity_string`, `get_staged_or_current_role`, `find_matching_node`, `print_cluster_layout`, `print_staging_role_changes`, `display_zone_redundancy`, and `parse_zone_redundancy`.

Control flow: show fetches layout, prints current roles, staged changes, and previewed post-apply layout. Assign resolves node patterns, handles replacement removals, derives zone/capacity/tags from args or current/staged role, and stages updates. Apply requires explicit version. Revert requires `--yes`. History prints version summaries and update trackers with guidance. Skip-dead-nodes sends version and missing-data flag, then reports tracker changes or actionable errors.

State and persistence: mutates cluster layout staging parameters, staged node roles, applied layout version, and tracker state through admin API. It does not directly persist local files.

Dependencies and integration points: uses admin layout API types, `bytesize`, `format_table`, shared remote API helper, and CLI structs. Cluster status code reuses layout display helpers.

Risks: node matching by prefix errors unless exactly one candidate matches; operators must pass the apply version to avoid accidental stale layout application. Capacity/tag inheritance logic is subtle when staging over existing staged roles. `parse_zone_redundancy` treats `none`, `max`, and `maximum` as maximum redundancy, which is semantically non-obvious.

Test signals: no direct tests; layout algorithm/API tests plus CLI smoke tests should cover staging, preview, apply version guard, revert guard, and prefix ambiguity.
