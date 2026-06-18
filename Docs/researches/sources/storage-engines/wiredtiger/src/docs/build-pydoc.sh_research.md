# sources/storage-engines/wiredtiger/src/docs/build-pydoc.sh

## Purpose
Builds Python API pydoc HTML for WiredTiger.

## APIs and control flow
The script computes `DOCS` from its own path, sets `TOP=$DOCS/..`, sources `$TOP/config.sh`, changes into `python`, and runs `pydoc -w wiredtiger` with `PYTHONPATH` pointing at `../../lang/python/src` and a Thrift Python 2.6 site-packages directory under `$THRIFT_HOME`.

## State, dependencies, integration, risks
It writes pydoc-generated HTML in the `python` directory. Dependencies are shell, `config.sh`, Python/pydoc, generated or source WiredTiger Python bindings, and Thrift environment variables. Risks are stale Python 2.6 Thrift path assumptions, execution from unexpected locations, missing `$THRIFT_HOME`, and pydoc importing code with side effects. Test signals are successful import of `wiredtiger` under the constructed `PYTHONPATH` and reproducible generated HTML.
