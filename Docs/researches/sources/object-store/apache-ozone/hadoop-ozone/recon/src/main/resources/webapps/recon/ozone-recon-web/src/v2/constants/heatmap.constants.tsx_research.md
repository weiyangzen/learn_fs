# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/constants/heatmap.constants.tsx

Purpose: Defines heatmap palette and allowed query dimensions for the Heatmap page.

Important APIs, types, and functions: Exports `colourScheme`, `TIME_PERIODS`, `ENTITY_TYPES`, and `ROOT_PATH`.

Control flow: Static constants only.

State and persistence behavior: No state.

Dependencies: No imports.

Integration points: Heatmap page and API query builders use these choices for time period, entity type, and root path.

Risks and edge cases: Arrays are plain strings rather than literal union types, so invalid consumer values are not prevented. Palette length must match heatmap bucket assumptions.

Test signals: Validate Heatmap controls only use these values and palette bucket count matches chart scale.
