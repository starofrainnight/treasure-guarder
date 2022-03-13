# -*- coding: utf-8 -*-

import github
from operator import attrgetter
from github import Github
from .repoapi import RepoApi
from typing import Dict
from attrdict import AttrDict
from github.GithubException import UnknownObjectException
from cachetools import cachedmethod


class GithubApi(RepoApi):
    def __init__(self, access_context) -> None:
        super().__init__(access_context)
        self._ctx = access_context

        kwargs = {"login_or_token": self._ctx["token"]}
        if "api-url" in self._ctx:
            kwargs["base_url"] = self._ctx["api-url"]

        self._github = Github(**kwargs)
        self._cache = dict()

    @cachedmethod(attrgetter("_cache"))
    def get_repo(self, owner: str, repo_name: str) -> Dict:
        github_repo = self._github.get_repo("%s/%s" % (owner, repo_name))

        repo = {"description": github_repo.description}
        return repo

    @cachedmethod(attrgetter("_cache"))
    def get_group(self, group: str) -> Dict:
        try:
            org = self._github.get_organization(group)
        except UnknownObjectException:
            self._github.get_user(group)
            org = AttrDict({"description": ""})

        info = {"description": org.description}
        return info
