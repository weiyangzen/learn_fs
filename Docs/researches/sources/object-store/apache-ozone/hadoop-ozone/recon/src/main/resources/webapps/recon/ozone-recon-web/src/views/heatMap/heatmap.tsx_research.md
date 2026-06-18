# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/heatMap/heatmap.tsx

Purpose: Legacy class-component Heatmap page. It fetches read-access data, normalizes node sizes, and renders an AG Charts treemap with path/entity/date filters.

Important APIs/types/functions: Defines heatmap response/state interfaces, module-level `minSize`/`maxSize`, `colourScheme`, and class methods `handleChange`, `handleSubmit`, `updateTreeMap`, `updateTreemapParent`, `disabledDate`, `resetInputpath`, `minmax`, `updateSize`, and `normalize`. Uses `AxiosGetHelper('/api/v1/heatmap/readaccess?...')`, `HeatMapConfiguration`, constants, Ant Design menus/date picker/result, and `showDataFetchError`.

Control flow: Mount fetches root/key/24H data. Filter changes call `updateTreeMap`, which sets loading, builds the query string, fetches data, computes min/max leaf sizes via `minmax`, recursively adds `normalizedSize`, and stores `treeResponse`. Fetch errors reset input/entity/date to empty strings, set endpoint failure, and mark Heatmap disabled on 404. Clicking a parent node updates the path and refetches. Render switches among loading, disabled, endpoint-failed, treemap, and no-data states.

State and persistence: Local state tracks loading, response, input path validity/help, entity type, date, endpoint failure, and Heatmap-enabled flag from route location state. Module globals hold min/max and cancellation controller. No persisted storage.

Dependencies and integration points: Integrates with the heatmap read-access endpoint, route location state from whatever page links to Heatmap, AG Charts configuration component, and backend-accepted time/entity constants.

Risks: Query params are not URL-encoded. `updateTreeMap` accepts `date: string` but state stores `string | number`. Catch block assumes `error.response.status`, which can fail for cancellation/network errors without response. `minmax` and `updateSize` mutate response data and use module-level bounds. Reset button only changes input path and does not refetch root immediately. Component reads `this.props.location` although props are typed generically.

Test signals: Tests should cover initial fetch, successful normalization, 404 disabled state, non-404 endpoint failure, filter/date changes, custom date restrictions, path validation, parent click refetch, cancellation on unmount, and no-data rendering.
