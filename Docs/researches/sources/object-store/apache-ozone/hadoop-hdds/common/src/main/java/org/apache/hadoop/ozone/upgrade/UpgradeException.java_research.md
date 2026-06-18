# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/upgrade/UpgradeException.java

## Purpose

`UpgradeException` is the structured `IOException` used by Ozone upgrade and finalization flows. It carries a `ResultCodes` enum so callers and clients can distinguish validation, finalization, and layout-version failures.

## APIs and control flow

Constructors support result-only, message, message-plus-cause, and cause-only forms. `getResult()` exposes the result code. `toString()` prefixes the standard exception string with the result code. `STATUS_CODE` is a string constant used for status-code serialization or parsing in adjacent code.

## State, dependencies, and integration

State is the final `ResultCodes result`. The enum includes `OK`, `INVALID_REQUEST`, layout update failure, feature finalization failure, pre-finalize action validation failure, first-upgrade-start action failure, and pre-finalize validation failure. It integrates with `UpgradeFinalization` and service-side upgrade managers.

## Risks and test signals

The result-only constructor has no message, so logs may depend on `toString()` to retain context. Tests should verify result preservation through all constructors, causal chain preservation, `toString()` format, and client handling for each result code.
