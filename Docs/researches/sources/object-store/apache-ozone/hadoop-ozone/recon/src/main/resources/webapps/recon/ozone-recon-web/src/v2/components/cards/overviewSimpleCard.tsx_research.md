# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/cards/overviewSimpleCard.tsx


Purpose: V2 simple metric card with icon, formatted numeric value, optional “View More” link, and error fallback.

Important APIs/types/functions: `IconSelector`, `OverviewSimpleCard`, icon map, and props for `icon`, `data`, `title`, `loading`, `hoverable`, `linkToUrl`, and `error`.

Control flow/state/persistence: On error returns compact `ErrorCard`; otherwise maps the icon string to AntD icon, formats `data` with `numberWithCommas`, and emits `data-testid="overview-${title}"`.

Dependencies/integration points: Used by V2 Overview metric cards and tested through Overview locators.

Risks/test signals: `data` is typed number, so string fallback like `N/A` must be handled before reaching this card. Unknown icons render question mark.
