## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/dev-support/findbugsExcludeFile.xml

Purpose: SpotBugs/FindBugs exclude-filter file for the `ozone-cli-shell` module.

Important structure and control flow: the XML defines an empty `<FindBugsFilter>`, meaning the module currently has no local suppressions. The `pom.xml` wires this file into the SpotBugs Maven plugin.

State and dependencies: build-time configuration only; no runtime state. Depends on the SpotBugs Maven plugin honoring `excludeFilterFile`.

Risks and test signals: an empty filter is a positive signal that warnings are not being locally suppressed. If future exclusions are added, they should be reviewed because they can hide shell command bugs.
