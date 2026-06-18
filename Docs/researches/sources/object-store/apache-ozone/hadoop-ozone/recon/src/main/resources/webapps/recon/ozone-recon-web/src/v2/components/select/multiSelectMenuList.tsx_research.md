# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/select/multiSelectMenuList.tsx

Purpose: Provides the custom `react-select` menu body used by `MultiSelect`, adding a search input and Select All/Unselect All row above options.

Important APIs, types, and functions: Exports `Option`, `MultiSelectInput`, and default `MultiSelectMenuList`. Reads extended data from `props.selectProps` rather than direct typed props.

Control flow: The input suppresses react-select blur while search is active. The menu computes `allSelected`, calls parent `customOnChange` with fixed plus selectable options, and closes/search-resets on outside blur or Escape.

State and persistence behavior: Only an input ref is local. Search term, menu open state, selected options, fixed options, and search-interaction ref are owned by `MultiSelect`.

Dependencies: Uses `react-select` `components` and raw inline styles.

Integration points: Tightly coupled to `MultiSelect`'s injected `selectProps` names and focus-management assumptions.

Risks and edge cases: Heavy `any` typing means missing selectProps fail at runtime. The 150ms blur timeout is race-prone. Checkbox `onChange={() => null}` relies on wrapper click handling for behavior.

Test signals: Exercise keyboard Escape, outside click while search is focused, Select All with zero selectable options, filtering plus select all, and fixed-option-only unselect behavior.
