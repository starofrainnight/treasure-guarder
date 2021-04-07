# -*- coding: utf-8 -*-

import github
from github import Github
from .repoapi import RepoApi
from typing import Dict


class GithubApi(RepoApi):
    def __init__(self, access_context) -> None:
        super().__init__(access_context)
        self._ctx = access_context

    def get_repo(self, owner: str, repo_name: str) -> Dict:
        kwargs = {"login_or_token": self._ctx["token"]}
        if "api-url" in self._ctx:
            kwargs["base_url"] = self._ctx["api-url"]

        g = Github(**kwargs)

        github_repo = g.get_repo("%s/%s" % (owner, repo_name))

        repo = {"description": github_repo.description}
        return repo
