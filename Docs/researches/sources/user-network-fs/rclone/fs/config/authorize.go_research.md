# sources/user-network-fs/rclone/fs/config/authorize.go

Purpose: implements `rclone authorize` for headless remote authorization, running a backend's post-config/OAuth flow locally and printing a token or encoded config blob for transfer.

Important APIs/functions: `Authorize(ctx, args, noAutoBrowser, templateFile) error`. It uses constants `ConfigAuthorize`, `ConfigAuthNoBrowser`, `ConfigTemplateFile`, `ConfigClientID`, `ConfigClientSecret`, and `ConfigToken`.

Control flow: the function suppresses confirmation and marks the context OAuth-only. It accepts one, two, or three args: backend type only, backend type plus base64 config map blob, or backend type plus client id/secret. It finds the backend, validates it has config support, builds an input `configmap.Simple`, decodes or sets extra parameters, creates a temporary remote name, builds a config mapper, replaces setters with an output map, calls `PostConfig`, then prints either the token or an encoded output blob.

State and persistence behavior: uses in-memory maps only and a temporary remote name `**temp-fs**`; it does not write normal config storage. Output is printed to stdout in a paste-delimited block. Context is modified to stop after OAuth where supported.

Dependencies and integration points: depends on backend registry lookup, `fs.ConfigMap`, `PostConfig`, `configmap.Simple.Encode/Decode`, and UI confirmation suppression. It integrates with OAuth-capable backends and remote machines that paste the resulting token/config.

Risks: assumes the backend writes `token` to the output map. Errors in encoded input blob or unsupported backend config are surfaced. The function prints sensitive token material to stdout by design.

Test signals: no direct test in this subset; behavior is partially covered by backend OAuth/config tests elsewhere.
