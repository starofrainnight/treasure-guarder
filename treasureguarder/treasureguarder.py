# -*- coding: utf-8 -*-

"""Main module."""

import os
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
                self._logger.info("Cached respository, updating")
                os.chdir(repo)
                run("git remote update")
            else:
                # Create a mirror clone of origin repository url if working
                # repository not exists.
                self._logger.info("New respository, cloning")

                run(
                    "git clone --mirror {url} {dirname}".format(
                        url=options["src"], dirname=repo
                    )
                )
                os.chdir(repo)

            self._logger.info("Check if remote exists")
            # Check if remote name exits
            p = run("git remote")
            remotes = p.stdout.splitlines()
            if self.REMOTE_NAME in remotes:
                self._logger.info("Remote '%s' exists" % self.REMOTE_NAME)

                # If the url already exists, we override it
                run(
                    "git config remote.{name}.url {url}".format(
                        name=self.REMOTE_NAME, url=options["dst"]
                    )
                )
            else:
                self._logger.info(
                    "Remote '%s' does not exists, add one" % self.REMOTE_NAME
                )
                # Add the remote url to this repository if it's not exists
                run(
                    "git remote add {name} {url}".format(
                        name=self.REMOTE_NAME, url=options["dst"]
                    )
                )

            self._logger.info("Fixs remote '%s'" % self.ORIGIN_NAME)

            run(
                "git config remote.{name}.url {url}".format(
                    name=self.ORIGIN_NAME, url=options["src"]
                )
            )

            self._logger.info(
                "Push all with tags to remote '%s'" % self.ORIGIN_NAME
            )

            # Push all to backup repository
            run("git push {name} --all".format(name=self.REMOTE_NAME))
            run("git push {name} --tags".format(name=self.REMOTE_NAME))

            self._logger.info("Done")
        finally:
            # Change back to original directory
            os.chdir(orig_dir)

    def exec_(self):
        os.makedirs(self.WORK_DIR, exist_ok=True)

        items = self._cfg.get("repos", list())
        count = len(items)
        i = 0
        for item in items:
            i += 1
            name = os.path.splitext(os.path.basename(item["src"]))[0]
            self._logger.info(
                "[%s/%s] Mirroring repository : %s" % (i, count, name)
            )
            self.mirror_repo(name, item)
