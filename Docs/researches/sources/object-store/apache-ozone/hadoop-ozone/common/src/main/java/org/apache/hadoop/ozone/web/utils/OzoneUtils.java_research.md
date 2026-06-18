# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/web/utils/OzoneUtils.java

Purpose: Common Ozone web/client utility functions for encoding, date formatting/parsing, request IDs, host names, resource-name validation, and time-duration config lookup.

Important APIs and types: Constants `ENCODING` and thread-local `DATE_FORMAT`; methods `verifyMaxKeyLength`, `getRequestID`, `getHostName`, `formatTime`, `formatDate`, `verifyResourceName`, `getTimeDuration`, and `getTimeDurationInMS`.

Control flow: `verifyMaxKeyLength` parses a string as positive integer and throws descriptive `IllegalArgumentException`s. Hostname lookup falls back to `localhost` on `UnknownHostException`. Date formatting/parsing uses a thread-local `SimpleDateFormat` configured with Ozone date format, US locale, and Ozone timezone. Time-duration lookup asks `ConfigurationSource` for the key in the default value's unit, then returns a Ratis `TimeDuration`.

State and persistence behavior: Holds a thread-local formatter; no persistence. Generated request IDs are random UUID strings.

Dependencies and integration points: Used by REST/web utilities and older client paths. Delegates resource-name validation to `HddsClientUtils`, uses `OzoneConsts`, configuration source, and Ratis time duration.

Risks: Error text says "digital" rather than "numeric", which may be user-visible. `verifyMaxKeyLength` takes a string and does not trim before parse. Date parsing is strict only to `SimpleDateFormat` defaults unless configured elsewhere; timezone is fixed by Ozone constants.

Test signals: Valid/invalid max key length, UUID format uniqueness, hostname fallback with mocked DNS failure, date format/parse round-trip in configured timezone, resource-name validation delegation, and duration unit conversion.
