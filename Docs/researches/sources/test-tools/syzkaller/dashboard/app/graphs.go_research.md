# sources/test-tools/syzkaller/dashboard/app/graphs.go

Purpose: prepares data for dashboard graph pages: kernel health, bug lifetimes, found bugs, manager fuzzing metrics, and crash statistics.

Important APIs/types/functions: `uiGraph`, `uiGraphHeader`, `uiGraphColumn`, `uiGraphValue`, `handleKernelHealthGraph`, `handleGraphLifetimes`, `handleFoundBugsGraph`, `handleGraphFuzzing`, `handleGraphCrashes`, `loadGraphBugs`, `loadStableGraphBugs`, `isStableBug`, `createBugsGraph`, `createFoundBugs`, `createBugLifetimes`, `createManagersGraph`, `extractMetric`, `createCrashesTable`, and `createCrashesGraph`.

Control flow: handlers build a common header, query bugs/jobs/manager stats, parse form filters, convert data into `uiGraph` or table structs, and render templates. Manager graphs prefill day columns, insert selected metrics, and normalize multi-metric output. Crash graphs compile regexps, count matching daily crashes, and convert to percentages.

State/persistence: read-only datastore access for `Bug`, `Job`, and child `ManagerStats`; no state writes.

Dependencies/integration: depends on UI template serving, namespace config, bug/reporting helpers, datastore, `managerList`, and `pkg/report/crash` classification.

Risks/test signals: regexps can be invalid or expensive; metric validation prevents panics in `extractMetric`; found-bugs projection assumes elapsed month duration; graph tests mostly check render success, with one bad-metric validation test.
