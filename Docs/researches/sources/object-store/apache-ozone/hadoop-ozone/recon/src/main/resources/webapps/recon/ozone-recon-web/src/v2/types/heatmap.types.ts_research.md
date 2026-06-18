# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/heatmap.types.ts

Purpose: Defines v2 heatmap input, response, and page-state types.

Important APIs/types/functions: Exports `InputPathValidTypes`, `HeatmapChild`, `InputPathState`, `HeatmapResponse`, `HeatmapState`, and `IResponseError`.

Control flow: Type-only module. It models a root response with min/max access counts and children, and leaf children with size/access/color fields.

State and persistence: No runtime state. `HeatmapState` covers the main page state while `InputPathState` covers form validation state.

Dependencies and integration points: Used by v2 heatmap page and heatmap plot components. `InputPathValidTypes` mirrors Ant Design `Form.Item` validation states.

Risks: `HeatmapChild` lacks optional `path`, `children`, and `normalizedSize` fields even though the page recursively traverses children and mutates `normalizedSize`. `IResponseError` is exported but unused in the v2 heatmap page import set. `date` is `string | number`, reflecting mixed period keys and custom Unix timestamps.

Test signals: Type tests or fixture-driven component tests should include nested child structures, zero-size children, custom timestamp dates, and invalid path states.
