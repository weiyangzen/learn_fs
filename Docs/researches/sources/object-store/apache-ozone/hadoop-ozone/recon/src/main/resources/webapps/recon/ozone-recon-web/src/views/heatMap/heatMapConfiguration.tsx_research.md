# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/heatMap/heatMapConfiguration.tsx

Purpose: Legacy AG Charts treemap configuration component for Heatmap data.

Important APIs/types/functions: Class component `HeatMapConfiguration` accepts `data`, `onClick`, and `colorScheme`; builds `AgChartsReact` options in constructor; defines `tooltipContent` for size/access/entity details.

Control flow: Constructor snapshots props into chart options. The treemap series uses `labelKey='label'`, `sizeKey='normalizedSize'`, `colorKey='color'`, a fixed color domain/range, custom tooltip renderer, and `nodeClick` listener. Clicking a non-leaf/group node with a `path` calls `props.onClick(path)`; leaf nodes with a truthy `color` do not trigger fetches.

State and persistence: Stores chart `options` in component state once. It does not update options if props change after construction unless remounted.

Dependencies and integration points: Depends on `ag-charts-react` and shared `byteToSize`. Used by legacy heatmap page after that page mutates API responses with `normalizedSize`.

Risks: Prop changes to `data` or `colorScheme` may not refresh the chart because options are initialized only in the constructor. The click logic treats falsy `color` as non-leaf; a leaf with color `0` may be misclassified. Tooltip content builds HTML strings from labels without escaping.

Test signals: Tests should cover initial render options, tooltip content for child and root nodes, click behavior for group versus leaf nodes including color `0`, and response to prop changes if component is refactored.
