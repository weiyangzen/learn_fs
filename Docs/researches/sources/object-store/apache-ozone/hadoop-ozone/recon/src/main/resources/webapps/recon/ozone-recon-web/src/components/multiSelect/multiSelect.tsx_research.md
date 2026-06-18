# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/components/multiSelect/multiSelect.tsx


Purpose: Legacy `react-select` multi-select wrapper with optional “Select all” support and compact value display.

Important APIs/types/functions: Exports `IOption` and `MultiSelect` `PureComponent`. Props extend `ReactSelectProps<IOption>` and add `allowSelectAll`, `allOption`, and `maxShowValues`.

Control flow/state/persistence: When select-all is enabled, custom `Option` renders checkboxes and custom `ValueContainer` shows “Select all” or `N selected`. `onChange` rewrites selections to include/drop the all option.

Dependencies/integration points: Used by legacy tables/forms needing column or filter selection; depends on `react-select` and animated components.

Risks/test signals: `components` object incorrectly includes `animatedComponents` as a key rather than spreading animated components. Non-null assertions around `onChange` assume controlled usage.
