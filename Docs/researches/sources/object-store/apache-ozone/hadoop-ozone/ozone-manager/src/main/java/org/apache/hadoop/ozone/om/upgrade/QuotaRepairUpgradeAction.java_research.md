## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/upgrade/QuotaRepairUpgradeAction.java

Purpose: upgrade action for the `QUOTA` layout feature that optionally recalculates quota usage during finalization.

Important APIs and types: annotated `@UpgradeActionOm(feature = QUOTA)` and implements `OmUpgradeAction`; `execute(OzoneManager)` reads `OZONE_OM_UPGRADE_QUOTA_RECALCULATE_ENABLE` and runs `QuotaRepairTask.repair`.

Control flow: if enabled, checks leader status, constructs a quota repair task, and runs repair. Non-leader or leader-not-ready exceptions are caught and logged so only the leader performs the repair during upgrade.

State and persistence: repair task updates quota usage metadata; this class itself stores nothing.

Dependencies and integration: discovered by `OMLayoutVersionManager` and invoked by `OMUpgradeFinalizer` when finalizing the `QUOTA` feature.

Risks and test signals: repair is skipped silently except for a warning on non-leaders, so clusters rely on leader finalization or manual CLI repair. Tests should cover config disabled, leader success, non-leader skip, leader-not-ready skip, repair exceptions propagating, and annotation/action registration.
