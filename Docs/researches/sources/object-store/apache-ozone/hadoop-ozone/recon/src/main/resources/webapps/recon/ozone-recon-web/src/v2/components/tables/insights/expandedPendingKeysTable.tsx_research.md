# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/insights/expandedPendingKeysTable.tsx

Purpose: Nested table for individual delete-pending key records under an aggregate pending-key row.

Important APIs, types, and functions: Exports `ExpandedPendingKeysTable`. Props include `DeletePendingKey[]` data and pagination config.

Control flow: Renders data size, replicated size, creation time, and modification time. Positive sizes are converted to human-readable strings while zero/negative values display raw.

State and persistence behavior: Stateless.

Dependencies: Uses AntD table, `byteToSize`, `getFormattedTime`, and insights types.

Integration points: Used by `DeletePendingKeysTable` as expanded-row detail content.

Risks and edge cases: Row key is `dataSize`, which can collide for multiple records with the same size. The render functions assign to their parameters and mix numeric/string return shapes.

Test signals: Cover duplicate sizes, zero/negative sizes, timestamp formatting, and parent pagination reuse.
