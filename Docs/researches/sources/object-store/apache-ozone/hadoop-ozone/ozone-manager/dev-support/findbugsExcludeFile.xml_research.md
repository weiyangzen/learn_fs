# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/dev-support/findbugsExcludeFile.xml

## Purpose

This SpotBugs/FindBugs exclusion file configures one module-specific suppression for the Ozone Manager module.

## Important APIs and Types

It has a `<FindBugsFilter>` root with one `<Match>` targeting class `org.apache.hadoop.ozone.om.snapshot.diff.delta.TestRDBDifferComputer` and bug pattern `RV_RETURN_VALUE_IGNORED_NO_SIDE_EFFECT`.

## Control Flow

No runtime control flow exists. Maven SpotBugs consumes the filter during static analysis.

## State and Persistence

No application state is affected. It persists a build-tool suppression.

## Dependencies and Integration Points

The OM POM references this file from the `spotbugs-maven-plugin` configuration.

## Risks and Edge Cases

Suppressions can mask real issues if the target class behavior changes. The suppression is class-specific, which limits blast radius.

## Test Signals

The relevant signal is SpotBugs running cleanly with the intended warning suppressed and unrelated warnings still reported.
