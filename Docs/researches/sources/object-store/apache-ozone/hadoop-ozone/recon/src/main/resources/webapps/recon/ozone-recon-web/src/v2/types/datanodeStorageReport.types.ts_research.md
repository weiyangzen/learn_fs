# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/datanodeStorageReport.types.ts

Purpose: Defines the storage-report shape used by the v2 Datanodes page.

Important APIs/types/functions: Exports `DatanodeStorageReport` with required Ozone-usable fields `capacity`, `used`, `remaining`, and `committed`, plus optional `reserved`, `minimumFreeSpace`, `filesystemCapacity`, `filesystemUsed`, and `filesystemAvailable`.

Control flow: Type-only module. The comments document the semantic distinction between Ozone-usable stats and raw filesystem stats.

State and persistence: No state. Optional fields allow older or partial backend responses.

Dependencies and integration points: Imported by datanode types and table/card components that display storage bars or detailed capacity fields.

Risks: Components must not assume optional raw filesystem fields exist. Numeric units are implied bytes but not enforced in type names. Backend field renames will surface as undefined values rather than compile errors if data is treated dynamically.

Test signals: Storage display tests should include responses with only required fields and responses with all optional raw/reserved fields.
