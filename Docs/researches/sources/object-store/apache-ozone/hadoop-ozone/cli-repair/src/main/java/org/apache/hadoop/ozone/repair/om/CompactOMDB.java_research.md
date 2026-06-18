## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/CompactOMDB.java

Purpose: online OM repair/admin command that asks a running OM to compact a named om.db column family asynchronously.

Important APIs and control flow: picocli requires `--column-family` and accepts optional `--service-id`/`--om-service-id` and `--node-id`. `execute` resolves `OMNodeDetails` from configuration, creates an `OMAdminProtocolClientSideImpl` proxy for the selected OM as the current user, calls `compactOMDB(columnFamilyName)`, and prints follow-up log guidance. Dry-run resolves inputs but skips the RPC.

State and dependencies: state changes occur inside the running OM process, not in this CLI process. Dependencies are `OzoneConfiguration`, OM admin protocol PB client, UGI, and `RepairTool`.

Risks and test signals: user-visible success only means request submission, not compaction completion. Incorrect node/service selection can compact an unintended OM. No direct test in this subset; `TestOzoneRepair` ensures leaf repair commands expose dry-run unless marked read-only.
