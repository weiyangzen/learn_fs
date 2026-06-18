# sources/object-store/garage/src/garage/cli/remote/bucket.rs

Purpose: implements remote CLI bucket management, permissions, website settings, quotas, incomplete-upload cleanup, and object inspection.

Important APIs/types/functions: `Cli::cmd_bucket` dispatcher; command methods for list/info/create/delete/alias/unalias/allow/deny/website/set-quotas/cleanup-incomplete-uploads/inspect-object; helper `print_bucket_info`.

Control flow: commands resolve buckets/keys through admin API search calls, then issue specific admin requests. Delete performs CLI-side checks that the target alias is the last global alias and that no local aliases remain, then requires `--yes`. Website mode requires exactly one of allow/deny. Quota parsing accepts byte sizes, object counts, and `"none"`. Object inspection prints per-version metadata, headers, and block list.

State and persistence: mutates bucket metadata, aliases, key permissions, website config, quotas, and incomplete upload records through admin API. Inspect/list/info are read-only.

Dependencies and integration points: uses `garage_api_admin::api`, `format_table`, chrono local formatting, `bytesize`, parse-duration, shared `Cli::api_request`, and key/bucket response structures. It is a major operator-facing integration with Garage's admin API.

Risks: many operations rely on server-side search uniqueness and response invariants. Delete's alias checks are client-side convenience and must remain aligned with server rules. Website update preserves previous error document only on allow when not explicitly provided. Cleanup loops buckets sequentially and partially completed multi-bucket cleanup can leave mixed results.

Test signals: no direct module tests; admin API and CLI smoke tests should exercise destructive guards, alias/permission changes, quota parsing, and object inspection formatting.
