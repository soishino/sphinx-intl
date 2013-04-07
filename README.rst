======================================================
sphinx-intl: translation support utility for Sphinx
======================================================

`sphinx-intl` is a utility tool that provides several features that make it easy to translate and to apply translation to Sphinx_ generated document. Optional: support the Transifex service for translation with Sphinx_ .


QuickStart for sphinx translation
===================================

This section describe to translate with Sphinx_ and `sphinx-intl` command.

1. Create your document by using Sphinx.

2. Add configurations to `conf.py`::

      locale_dirs = ['locale/']   #path is example but recommended.
      gettext_compact = False     #optional.

   `locale_dirs` is essential and `gettext_compact` is optional.

3. Build document's pot files::

      $ make gettext

4. Setup/Update your `locale_dirs`::

      $ sphinx-intl update -l de,ja

   Done. You got these directories that contain po files:

   * `./locale/pot/`
   * `./locale/de/LC_MESSAGES/`
   * `./locale/ja/LC_MESSAGES/`

5. Translate your po files under `./locale/<lang>/LC_MESSAGES/`.

6. Make translated document::

      $ sphinx-intl build
      $ make -e SPHINXOPTS="-D language='ja'" html

That's all!


Basic Features
===============

* create or update po files from pot files.
* build mo files from po files.

Requirements
--------------

- Python 2.5, 2.6, 2.7, 3.1, 3.2, 3.3.
- external library: polib_


Optional features
==================
These features need `transifex_client`_ library.

* create .transifexrc file from environment variable, without interactive input.
* create .tx/config file without interactive input.
* update .tx/config file from locale/pot files automatically.
* build mo files from po files in the locale directory.

You need to use `tx` command for below features:

* `tx push -s` : push pot (translation catalogs) to transifex.
* `tx pull -l ja` : pull po (translated catalogs) from transifex.

Requirements
--------------

- Python 2.5, 2.6, 2.7. (depends transifex_client that only support 2.x)

- Your transifex_ account if you want to download po files from transifex
  or you want to translate on transifex.

- external library: `transifex-client`_



Installation
=============

Recommend strongly: use virtualenv for this procedure::

   $ pip install https://bitbucket.org/shimizukawa/sphinx-intl/get/default.zip

If you want to use `Optional Features`_, you need install additional library::

   $ pip install transifex-client


Commands, options, environment variables
=========================================

Type `sphinx-intl` without arguments, options to show command help.


Setup environment variables
==============================

All command-line options can be set with environment variables using the format SPHINXINTL_<UPPER_LONG_NAME> . Dashes (-) have to replaced with underscores (_).

For example, to set the locale dirs::

   export SPHINXINTL_LOCALE_DIRS=locale

This is the same as passing the option to sphinx-intl directly::

   sphinx-intl --locale-dirs=locale <command>


Setup sphinx conf.py
======================

Add below settings to sphinx document's conf.py if not exists::

   locale_dirs = ['locale/']   #for example
   gettext_compact = False     #optional

.. _Sphinx: http://sphinx-doc.org
.. _transifex: https://transifex.com
.. _`transifex-client`: https://pypi.python.org/pypi/transifex-client
.. _polib: https://pypi.python.org/pypi/polib
