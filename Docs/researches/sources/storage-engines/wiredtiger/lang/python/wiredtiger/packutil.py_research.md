# sources/storage-engines/wiredtiger/lang/python/wiredtiger/packutil.py

This module provides byte/string compatibility helpers and constants for the packing modules. It defines `x00`, `xff`, `x00_entry`, `xff_entry`, and `empty_pack`, then selects Python 3 or Python 2 helper implementations for `_ord`, `_chr`, `_is_string`, and `_string_result`.

It is stateless and depends only on `sys`. `packing.py` and `intpacking.py` use it to hide byte representation differences. Risks include historical Python 2 code despite package-level Python 3 rejection, default UTF-8 decoding in `_string_result`, and `_chr` supporting only one or two byte arguments. Tests should check helper return types, constants, `_chr`, `_ord`, and decoding behavior.
