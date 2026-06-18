# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/net/TestNetUtils.java

## Purpose
Tests normalization behavior in SCM network utility code.

## Important APIs, types, and functions
- Exercises `NetUtils.normalize` style behavior for network paths or node names.
- Uses JUnit assertions for normalized output variants.

## Control flow
The test feeds representative strings into the normalize function and asserts canonical output, including handling of separators or empty/default path shapes.

## State and persistence behavior
Pure string transformation; no state persists.

## Dependencies and integration points
SCM topology and placement code depend on stable network-location normalization.

## Risks and test signals
Incorrect normalization can misplace nodes in topology trees. This file signals canonical path formatting behavior.
