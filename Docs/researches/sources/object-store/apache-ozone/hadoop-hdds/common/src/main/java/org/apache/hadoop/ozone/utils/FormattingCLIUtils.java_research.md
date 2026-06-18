# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/utils/FormattingCLIUtils.java

## Purpose

`FormattingCLIUtils` renders centered ASCII tables for Ozone CLI output. It supports an optional title, header rows, and data rows with computed column widths.

## APIs and control flow

Construction initializes an internal `StringBuilder`, row list, and max-column map. `addHeaders` and `addLine` append rows after converting values to strings and updating column widths. `appendRows` rejects a row with fewer columns than previously seen, but it permits more columns and expands the table. `render()` calls `buildTable`, which emits title, borders, headers, and data lines. `StrUtils` provides center, left-pad, right-pad, and repeat helpers.

## State, dependencies, and integration

State is mutable table content and a builder reused during rendering. There are no external dependencies. It integrates with command-line tools that need human-readable table output.

## Risks and test signals

`render()` is not idempotent because it appends to the same builder each call. All padding uses Java string length, not display width, so wide Unicode or ANSI escape sequences will misalign. Tests should cover title truncation, column mismatch behavior, null values, multiple headers, no rows, and repeated render calls.
