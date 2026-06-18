# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/utils/common.tsx


Purpose: Shared formatting, error notification, comparison, merge, and promise-result helpers.

Important APIs/types/functions: Exports `getCapacityPercent`, `timeFormat`, `showInfoNotification`, `showDataFetchError`, `byteToSize`, `numberWithCommas`, `nullAwareLocaleCompare`, `removeDuplicatesAndMerge`, and `checkResponseError`.

Control flow/state/persistence: Error handler suppresses canceled axios requests, formats server/network errors, emits AntD error notifications, and turns metadata initialization strings into warn notifications. `checkResponseError` scans `Promise.allSettled` results and either throws cancellation or reports failures.

Dependencies/integration points: Used broadly by navbars, storage/quota bars, metadata, tests, and API hooks.

Risks/test signals: `getCapacityPercent` has no zero guard. `removeDuplicatesAndMerge` indexes generic objects by string without constraints. Tests spy on `showDataFetchError` for API failures.
