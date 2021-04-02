# -*- coding: utf-8 -*-

"""Main module."""

import os
import invoke
import yaml
import logging
import click
from attrdict import AttrDict
from typing import Dict, Any
from invoke import run


class TreasureGuarder(object):
    REMOTE_NAME = "tgremote"
    ORIGIN_NAME = "origin"
    WORK_DIR = ".tgwork"

    def __init__(self, kwargs):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._args = AttrDict(kwargs)
        if os.path.exists(self._args.cfg_path):
            with open(self._args.cfg_path, "r") as f:
                self._cfg = yaml.safe_load(f)
        else:
            self._cfg = dict()

    def mirror_repo(self, repo: str, options: Dict[str, Any]):
        local_repo_dir = os.path.join(self.WORK_DIR, repo)
        os.makedirs(local_repo_dir, exist_ok=True)

        # Prepare the original directory and changed to work directory
        orig_dir = os.path.realpath(os.curdir)
        os.chdir(self.WORK_DIR)
        try:
            # TODO: We must parse the LFS objects either.
            if os.path.exists(os.path.join(repo, "packed-refs")):
                os.chdir(repo)
                run("git remote update")
            else:
                # Create a mirror clone of origin repository url if working
                # repository not exists.
                run(
                    "git clone --mirror {url} {dirname}".format(
                        url=options["src"], dirname=repo
                    )
                )
                os.chdir(repo)

            # Check if remote name exits
            p = run("git remote")
            remotes = p.stdout.splitlines()
            if self.REMOTE_NAME in remotes:
                # If the url already exists, we override it
                run(
                    "git config remote.{name}.url {url}".format(
                        name=self.REMOTE_NAME, url=options["dst"]
                    )
                )
            else:
                # Add the remote url to this repository if it's not exists
                run(
                    "git remote add {name} {url}".format(
                        name=self.REMOTE_NAME, url=options["dst"]
                    )
                )

            run(
                "git config remote.{name}.url {url}".format(
                    name=self.ORIGIN_NAME, url=options["src"]
                )
            )

            # Push all to backup repository
            run("git push {name} --all".format(name=self.REMOTE_NAME))
            run("git push {name} --tags".format(name=self.REMOTE_NAME))
        finally:
            # Change back to original directory
            os.chdir(orig_dir)

    def exec_(self):
        os.makedirs(self.WORK_DIR, exist_ok=True)

        items = self._cfg.get("repos", dict()).items()
        count = len(items)
        i = 0
        for k, v in items:
            i += 1
            click.echo(
                "\n[%s/%s] Mirroring repository : %s ..." % (i, count, k)
            )
            self.mirror_repo(k, v)
