# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/select/multiSelect.tsx

Purpose: Wraps `react-select` as Recon's multi-column/filter selector with checkboxes, fixed non-removable options, optional embedded search, and optional select-all behavior.

Important APIs, types, and functions: Exports `MultiSelect` and re-exports `Option`. Props extend `react-select` multi props and add `selected`, `fixedColumn`, `columnLength`, `showSearch`, `showSelectAll`, `onChange`, and `onTagClose`.

Control flow: Normalizes fixed columns, filters selectable options by local search, renders a custom value container showing selected counts, and delegates menu rendering to `MultiSelectMenuList`. Selection always re-adds fixed options before notifying the parent.

State and persistence behavior: Tracks local `searchTerm` and menu open state; refs track search interaction and the containing DOM node. Selected options are controlled by the parent.

Dependencies: Uses `react-select`, shared `selectStyles`, and the sibling custom menu/input components.

Integration points: Used by Buckets, Containers, Datanodes, Pipelines, Volumes, and plots to control visible table columns or high-cardinality filters.

Risks and edge cases: `filteredOptions` omits `selectableOptions` from its dependency list and uses `options` instead, which can be stale. DOM access to `document.body` assumes browser runtime. The value-container child-name check depends on react-select internals.

Test signals: Cover fixed columns surviving unselect-all, select-all including fixed options, search focus not closing the menu, option list updates after props change, disabled state, and portal rendering.
