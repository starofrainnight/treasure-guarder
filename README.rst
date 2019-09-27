================
treasure-guarder
================

.. image:: https://img.shields.io/pypi/v/treasure-guarder.svg
    :target: https://pypi.python.org/pypi/treasure-guarder

.. image:: https://travis-ci.org/starofrainnight/treasure-guarder.svg?branch=master
    :target: https://travis-ci.org/starofrainnight/treasure-guarder

.. image:: https://ci.appveyor.com/api/projects/status/github/starofrainnight/treasure-guarder?svg=true
    :target: https://ci.appveyor.com/project/starofrainnight/treasure-guarder

A python script for backup repositories to custom git server

* License: Apache-2.0
* Documentation: https://treasure-guarder.readthedocs.io.

Usage
--------

* Prepare your working directory, for example : `/opt/tg-workspace`
    treasure-guarder will create a cache directory `.tgwork` under `/opt/tg-workspace`
* Create a configure file `treasure-guarder.yml` under `/opt/tg-workspace` just like:

 ::

    repos:
      treasure-guarder:
        from: https://github.com/starofrainnight/treasure-guarder.git
        to: ssh://git@localhost/github/starofrainnight/treasure-guarder.git
      abhealer:
        from: https://github.com/starofrainnight/abhealer.git
        to: ssh://git@localhost/github/starofrainnight/abhealer.git
        
* Then run this command in your console under directiry `/opt/tg-workspace`

 ::

    treasure-guarder ./treasure-guarder.yml

**NOTICE:**

1. Ensure latest git command exists in your shell environment
2. Ensure you have rights to access to the source repository and the destination repository
3. Ensure there won't prompt password when pushing to destination repository
4. Normally, the cache directory `.tgwork` will created under current working directory


Credits
---------

This package was created with Cookiecutter_ and the `PyPackageTemplate`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`PyPackageTemplate`: https://github.com/starofrainnight/rtpl-pypackage

