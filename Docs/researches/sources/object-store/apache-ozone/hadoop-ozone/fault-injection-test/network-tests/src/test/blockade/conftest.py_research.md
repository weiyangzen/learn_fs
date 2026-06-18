<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/conftest.py -->
# sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/conftest.py

Final split target: `Docs/researches/sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/conftest.py_research.md`.

## Purpose
Pytest configuration for Ozone network/blockade tests, adding first/second phase selection, rewriting report statuses for skipped phases, and collecting Docker logs at session end. The file has 113 lines and was read in full for this research pass.

## Important APIs, Types, And Functions
Python hooks/functions: `pytest_addoption, run_second_phase, pytest_configure, pytest_report_teststatus, pytest_sessionfinish, gather_docker_logs`; imports include `
import logging, import os, import time, import subprocess, import pytest`.

## Control Flow
Pytest calls these hook functions during option parsing, configuration, report rendering, session finish, and log collection; phase options alter skip/report semantics before final status accounting.

## State And Persistence Behavior
State is pytest configuration/options, per-report outcome metadata, terminal status output, and Docker log files gathered at session finish.

## Dependencies And Integration Points
imports `
import logging`, `import os`, `import time`, `import subprocess`, `import pytest`; tools `docker`, `pytest`.

## Risks And Edge Cases
- Assertions focus on visible behavior in this file; regressions outside the covered cases may need broader tests.
- Shared static fixtures can make test order and mutation restoration important.

## Test Signals
Signals come from chaos-test completion, propagated future exceptions, JUnit assertions in `LoadBucket`, mini-cluster readiness waits, and generated test reports.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/conftest.py -->
