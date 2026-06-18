## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/OzoneInteractiveWelcome.java

Purpose: builds startup banner lines for the Ozone interactive shell.

Important APIs and control flow: `lines` loads `OzoneConfiguration`, reads Ozone version/release, formats configured OM and SCM endpoints, and appends help/exit/completion hints. `formatOmEndpoints` uses HA service IDs if present, otherwise the direct OM address; failures produce a configuration hint. `formatScmEndpoints` formats SCM client addresses similarly.

State and dependencies: no persistence; reads current process configuration. Depends on `OzoneVersionInfo`, `HddsUtils`, `OmUtils`, and OM/SCM config keys.

Risks and test signals: banner endpoint output is diagnostic only, but misleading configuration handling can confuse interactive users. No direct tests in this subset.
