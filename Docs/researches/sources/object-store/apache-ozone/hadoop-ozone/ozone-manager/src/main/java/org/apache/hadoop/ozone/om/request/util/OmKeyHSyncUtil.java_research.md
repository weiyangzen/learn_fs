
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/util/OmKeyHSyncUtil.java

Purpose: Provides helper logic to detect whether a key has already been hsync'ed by the same client and can avoid an extra open-key table update.

Important APIs and types: Static utility; uses `OmKeyInfo.getMetadata`, `OzoneConsts.HSYNC_CLIENT_ID`, and SLF4J logging.

Control flow: `isHSyncedPreviously` reads the previous hsync client ID metadata. It returns true when it matches the current client ID, logs a warning when a different previous client ID is found, and otherwise returns false.

State and persistence behavior: No direct mutation. It reads `OmKeyInfo` metadata that is persisted by key commit/hsync handlers.

Dependencies and integration points: Used by OM key write/hsync request paths to reduce redundant DB writes while preserving client ownership diagnostics.

Risks: Mismatched client IDs are only warned, not rejected, so callers must enforce any stronger semantics. Tests should cover no metadata, matching metadata, and mismatch logging/false result.
