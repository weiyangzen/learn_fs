# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/utils/clipboard.ts


Purpose: Cross-context clipboard copy helper.

Important APIs/types/functions: Exports async `copyToClipboard(text): Promise<boolean>`.

Control flow/state/persistence: Tries `navigator.clipboard.writeText`; on denial/unavailability falls back to creating a hidden readonly textarea, selecting it, and calling `document.execCommand('copy')`. Cleans up the textarea on normal fallback path.

Dependencies/integration points: Used by UI controls that copy IDs, paths, or generated assistant text, especially on HTTP clusters where async Clipboard API may be unavailable.

Risks/test signals: If `execCommand` throws after append but before removal, textarea cleanup is skipped. No direct tests in this subset.
