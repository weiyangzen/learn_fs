# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/locators/locators.ts


Purpose: Centralizes `data-testid` strings and row-test regular expressions used by Recon web tests.

Important APIs/types/functions: Exports `overviewLocators`, `datanodeLocators`, `pipelineLocators`, `autoReloadPanelLocators`, and `searchInputLocator`. Includes helper functions for datanode and pipeline row IDs.

Control flow/state/persistence: No runtime state; constants only.

Dependencies/integration points: Tests depend on these constants matching V2 Overview, Datanodes, Pipelines, AutoReloadPanel, and search components. Regex entries are passed to `screen.getAllByTestId`.

Risks/test signals: Typos such as `datanodeSearchcDropdown` are harmless only while unused. Any production `data-testid` rename must update this file and related tests together.
