## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/resources/webapps/hddsDatanode/dn.js

Purpose: `dn.js` defines AngularJS modules, routes, controllers, filters, and formatting helpers for the HDDS datanode web UI.

Important APIs and functions: it creates module `dn` depending on `ozone` and `nvd3`, registers `dnOverview`, adds routes `/iostatus` and `/dn-scanner`, defines `IOStatusController`, `DNScannerController`, filters `millisecondsToMinutes` and `twoDecimalPlaces`, and helper functions `transform()` and `convertTimestampToDate()`.

Control flow and state: `dnOverview` fetches JMX volume metrics and SCM connection manager metrics. It transforms byte-size fields to human-readable units and converts heartbeat timestamps from seconds since epoch to local date-time strings. IO status and scanner controllers fetch their respective JMX beans into controller fields. Filters defensively return `Invalid input` for `NaN`.

Persistence and integration: all state is client-side view model data fetched from datanode JMX endpoints. The file integrates with Angular route templates `dn-overview.html`, `iostatus.html`, and `dn-scanner.html`, plus JMX bean naming conventions.

Risks and test signals: there is no error handling for failed `$http` requests. `transform()` loops while `Math.floor(v) > 0`, so zero and non-numeric inputs can produce odd output. Timestamp formatting uses browser local time. The use of arrow functions and template literals requires browser support despite AngularJS age. No tests are in this subset.
