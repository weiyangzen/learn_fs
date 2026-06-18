# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/ReconUpgradeAction.java

Purpose: `ReconUpgradeAction` is the single-method interface for code that runs during Recon layout feature finalization.

Important APIs and types: `execute(DataSource source) throws Exception` gives actions access to the Recon SQL datasource and lets them throw failures to the layout manager.

Control flow and integration: action classes are annotated with `@UpgradeActionRecon`; `ReconLayoutFeature.registerUpgradeActions` instantiates them; `ReconLayoutVersionManager.finalizeLayoutFeatures` invokes `execute`.

State and persistence: no state in the interface. Implementations may alter SQL schema, update data, or trigger controller rebuilds.

Dependencies: `javax.sql.DataSource`.

Risks and test signals: implementations need clear transaction expectations because the manager also manages a connection. Tests should assert that failing actions propagate exceptions unless an implementation deliberately logs and suppresses them.
