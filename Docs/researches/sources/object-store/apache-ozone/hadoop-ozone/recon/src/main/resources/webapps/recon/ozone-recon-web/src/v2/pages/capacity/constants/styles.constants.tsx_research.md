# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/capacity/constants/styles.constants.tsx

Purpose: Shared React CSS style objects for capacity cards and statistics.

Important APIs, types, and functions: Exports `cardHeadStyle` and `statisticValueStyle`.

Control flow: Static style objects only.

State and persistence behavior: No state.

Dependencies: Uses React CSSProperties type implicitly through `React.CSSProperties`.

Integration points: Imported by CapacityBreakdown and CapacityDetail.

Risks and edge cases: The file references `React.CSSProperties` without importing React, which relies on global JSX/React type availability and can fail under stricter TS settings. Styles hard-code Roboto/colors.

Test signals: Typecheck under project TS config and visual regression for card headers/statistics.
