# sources/sync-backup/kopia/internal/server/api_sources.go

Purpose: implements APIs for listing known snapshot sources and creating/refreshing a source manager.

Important APIs/types/functions: `handleSourcesList` and `handleSourcesCreate`.

Control flow: list snapshots all current source managers and returns their source/status/counters. Create decodes a source request, ensures a manager exists for the source, refreshes status, and returns the updated source list or source response.

State and persistence behavior: source managers are runtime server state; source creation may cause manager startup but does not by itself write a snapshot.

Dependencies and integration points: bridges UI source pages, `sourceManager`, repository source lists, and scheduler refresh.

Risks and test signals: source manager lifecycle must be synchronized with repository refresh and policy changes. Tests cover snapshot counters and policy-triggered refresh.
