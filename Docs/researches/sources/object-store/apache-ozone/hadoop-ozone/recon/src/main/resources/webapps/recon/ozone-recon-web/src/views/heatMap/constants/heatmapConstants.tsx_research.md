# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/heatMap/constants/heatmapConstants.tsx

Purpose: Legacy heatmap constants module.

Important APIs/types/functions: Exports `TIME_PERIODS = ['24H','7D','90D']`, `ENTITY_TYPES = ['key','bucket','volume']`, and `ROOT_PATH = '/'`.

Control flow: Constant-only module; no logic.

State and persistence: No state. Arrays are mutable at runtime despite TypeScript annotations.

Dependencies and integration points: Imported by legacy heatmap page for default state and menu keys. Values must match backend accepted `startDate` period strings and `entityType` query values.

Risks: Backend enum/period changes require updating this module and any v2 counterpart constants. Mutable arrays can be altered by consumers unless treated read-only by convention.

Test signals: Heatmap menu tests should verify all constants appear in the UI and are accepted by request construction.
