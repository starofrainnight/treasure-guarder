# -*- coding: utf-8 -*-

"""Main module."""

import re
import os
import yaml
import logging
import click
import invoke
from attrdict import AttrDict
from typing import Dict, Any, Tuple
from . import repoapi


def run(command, **kwargs):
    logging.info("[CMD] %s" % (command,))
    return invoke.run(command, **kwargs)


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

    def get_domain_from_url(self, url):
        # type: (str) -> str
        from urllib.parse import urlsplit

        if "://" in url:
            urlpath = urlsplit(url).netloc
        else:
            urlpath = url.split("/")[0]

        domain = urlpath.split(":")[0]
        domain = domain.split("@")
        if len(domain) >= 2:
            domain = domain[1]
        else:
            domain = domain[0]

        return domain

    def get_owner_repo_from_url(self, url):
        # type: (str) -> Tuple[str, str]
        from urllib.parse import urlsplit

        url = os.path.splitext(url)[0]
        repo = os.path.basename(url)
        url = os.path.dirname(url)
        owner = os.path.basename(url).split(":")[-1]

        return (owner, repo)

    def _mirror_info(self, src_url, dst_url):
        access_ctxs = self._cfg.get("access-contexts", dict())
        src_domain = self.get_domain_from_url(src_url)
        dst_domain = self.get_domain_from_url(dst_url)
        # if src_domain in access_ctxs:

        # Create repository to destination if we have supports
        if dst_domain not in access_ctxs:
            return

        logging.info("src_url: %s" % src_url)
        logging.info("dst_url: %s" % dst_url)

        dst_owner, dst_repo = self.get_owner_repo_from_url(dst_url)
        dst_api = repoapi.get(access_ctxs[dst_domain])

        try:
            dst_api.get_repo(dst_owner, dst_repo)
            self._logger.info("Repo '%s/%s' exists" % (dst_owner, dst_repo))
        except repoapi.RepoApiError:
            # No specific repo found
            self._logger.info("Create repo '%s/%s'" % (dst_owner, dst_repo))
            dst_api.create_repo(dst_owner, dst_repo)

        if src_domain not in access_ctxs:
            self._logger.info("No source description")
            return

        src_api = repoapi.get(access_ctxs[src_domain])

        src_owner, src_repo = self.get_owner_repo_from_url(src_url)
        src_repo_info = src_api.get_repo(src_owner, src_repo)
        src_desc = src_repo_info["description"]
        src_desc = "" if src_desc is None else src_desc.strip()

        dst_repo_info = dst_api.get_repo(dst_owner, dst_repo)
        dst_desc = dst_repo_info["description"]
        dst_desc = "" if dst_desc is None else dst_desc.strip()

        if src_desc == dst_desc:
            self._logger.info("Description is same")
            return

        if len(src_desc.strip()) <= 0:
            self._logger.info("Source description is empty!")
            return

        print("set '%s/%s' to '%s'" % (dst_owner, dst_repo, src_desc))

        dst_api.edit_repo(dst_owner, dst_repo, src_desc)

    def mirror_repo(self, repo: str, options: Dict[str, Any]):
        self._mirror_info(options["src"], options["dst"])

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

        pat = r"(?:(?:ssh|http|https)\:\/\/)?(?:[\w\.\-]+@)?[\w\.\-]+\:(?:\d+\/(.*)|([^/]+\/.*))"

        items = self._cfg.get("repos", list())
        count = len(items)
        i = 0
        for item in items:
            i += 1

            matched = re.match(pat, item["src"])

            if matched.group(1) is None:
                name = matched.group(2)
            else:
                name = matched.group(1)
            name = name.replace("/", "-")
            name = os.path.splitext(name)[0]

            self._logger.info(
                "[%s/%s] Mirroring repository : %s" % (i, count, name)
            )

            self.mirror_repo(name, item)
