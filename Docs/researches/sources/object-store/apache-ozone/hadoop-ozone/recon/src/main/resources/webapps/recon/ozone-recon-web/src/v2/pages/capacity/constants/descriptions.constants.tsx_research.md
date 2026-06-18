# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/capacity/constants/descriptions.constants.tsx

Purpose: Holds explanatory copy for Capacity page tooltips.

Important APIs, types, and functions: Exports `totalCapacityDesc`, `otherUsedSpaceDesc`, `ozoneUsedSpaceDesc`, `datanodesPendingDeletionDesc`, and `nodeSelectorMessage`.

Control flow: Static string constants only.

State and persistence behavior: No state.

Dependencies: No imports.

Integration points: Consumed by Capacity page labels and `WrappedInfoIcon` tooltips.

Risks and edge cases: Descriptions must remain accurate as backend semantics evolve; `totalCapacityDesc` is exported here but Capacity also defines a JSX variable with the same conceptual name.

Test signals: Content snapshot in Capacity tooltips and review when capacity API definitions change.
