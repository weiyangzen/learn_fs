# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/420

Purpose: Linux reporter parse fixture for syzkaller. This file has no expectation headers and acts as a negative/no-crash fixture. Its five body lines must not produce a parsed crash.

Important APIs, types, and functions: it still runs through the same report test harness, especially `ContainsCrash` and `Parse`, but expected title/type are empty. No stack frames or crash-specific functions are present.

Control flow: the harness reads the file, finds no `TITLE:` header, and expects the Linux reporter not to report a crash from the remaining text. This validates that incidental console text does not trigger an oops matcher.

State and persistence behavior: the fixture stores absence of expectations as its state. Parser runtime state should remain empty or no-crash.

Dependencies, integration points, risks, and test signals: this protects false-positive resistance in syzkaller's Linux report parser. The risk is broadening regexes so ordinary lines become a crash. Passing tests require `ContainsCrash` false and no non-empty parsed report/title.
