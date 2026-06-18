# sources/test-tools/syzkaller/dashboard/app/kcidb.go

Purpose: cron-driven publication of eligible syzkaller dashboard bugs to KCIDB.

Important APIs/types/functions: `initKcidb`, `handleKcidbPoll`, `handleKcidbNamespce`, and `publishKcidbBug`.

Control flow: cron handler iterates namespaces with KCIDB config, creates a `kcidb.Client`, scans open bugs, publishes up to 30 eligible bugs, and logs namespace failures without stopping other namespaces.

State/persistence: mutates `Bug.KcidbStatus`: non-zero statuses skip future attempts, `1` means published, `2` means not publishable due to missing critical report data. External side effect is KCIDB publish.

Dependencies/integration: depends on `pkg/kcidb`, namespace `KcidbConfig`, bug scanning/report loading, access sanitization, final reporting state, datastore transactions, and App Engine cron routing.

Risks/test signals: status update after external publish can fail and allow duplicate attempts; status `2` prevents retry if missing data later appears; no direct subset tests cover eligibility or publish failure paths.
