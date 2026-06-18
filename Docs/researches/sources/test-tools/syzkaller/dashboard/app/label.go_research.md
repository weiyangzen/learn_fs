# sources/test-tools/syzkaller/dashboard/app/label.go

Purpose: defines bug labels, dynamic validation rules, help text, and mutation/query helpers.

Important APIs/types/functions: label constants such as `SubsystemLabel`, `PriorityLabel`, `NoRemindersLabel`, `OriginLabel`, `MissingBackportLabel`, `RaceLabel`, `ActionableLabel`; `BugPrio`; rule types `oneOf`, `subsetOf`, `trueFalse`; `makeLabelSet`, `labelSet.ValidateValues`, `labelSet.Help`, `Bug.HasLabel`, `Bug.LabelValues`, `Bug.SetLabels`, `Bug.UnsetLabels`, `Bug.HasUserLabel`, `Bug.prio`, and `BugPrio.LessThan`.

Control flow: `makeLabelSet` builds allowed labels from namespace config, subsystem service data, repo origin labels, and KCSAN title classification. `SetLabels` validates one label type at a time, replaces existing labels of that type, and appends new values.

State/persistence: labels persist on `Bug.Labels`; `SetBy` distinguishes manual from automatic labels.

Dependencies/integration: depends on namespace config, subsystem service, `pkg/report/crash`, `subsystemListURL`, and entity helpers; used by reporting, subsystem reminders, tree-origin, Linux reporting, and UI filters.

Risks/test signals: unknown labels validate as no-op unless callers separately check `FindLabel`; unknown priority values get zero ordering. Covered indirectly by subsystem/Linux/tree/UI tests.
