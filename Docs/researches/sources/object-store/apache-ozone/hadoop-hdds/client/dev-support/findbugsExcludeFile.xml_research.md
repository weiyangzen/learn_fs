# sources/object-store/apache-ozone/hadoop-hdds/client/dev-support/findbugsExcludeFile.xml

Purpose: SpotBugs filter for the `hdds-client` module.

Important APIs/types/functions: Contains one `<Match>` suppressing `EI_EXPOSE_REP2` for `org.apache.hadoop.hdds.scm.storage.ByteArrayReader`, with a comment that deep-copying `byte[]` would hurt performance.

Control flow: The client module POM passes this filter to SpotBugs during static analysis.

State and persistence behavior: Static build-time configuration only.

Dependencies and integration points: Integrated through the `spotbugs-maven-plugin` configuration in `client/pom.xml`.

Risks: Suppression applies only to a specific class not otherwise included in this work item. If the class moves or behavior changes, the stale filter may hide or fail to hide the intended warning.

Test signals: SpotBugs output should show this one intentional suppression and no broad class of hidden warnings.
